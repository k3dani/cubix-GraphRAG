"""Neo4j-kapcsolat, a gráfséma gépi változata és idempotens író (leírás: docs/schema.md)."""

import re
from collections import defaultdict
from datetime import date

from neo4j import Driver, GraphDatabase, ManagedTransaction

from graphrag_course import config

# címke → egyedi kulcs-tulajdonság; mindegyikre uniqueness constraint kerül
NODE_KEYS = {
    # dokumentumgráf (extrakció nélkül, a korpusz szerkezetéből)
    "Document": "doc_id",
    "Section": "section_id",
    "Chunk": "chunk_id",
    # szakterületi gráf (most a seed tölti, a 3. héttől az LLM-es kinyerés)
    "Company": "reg_no",
    "Person": "person_id",
    "Address": "address",
    "Activity": "code",
    "BankAccount": "number",
    "VatGroup": "group_tax_id",
    "Contract": "contract_id",
    "Invoice": "invoice_id",
    "Project": "project_id",
    "InsolvencyProceeding": "case_no",
    "Financials": "financials_id",
}

# éltípus → (megengedett kezdő címkék, megengedett végcímkék, időbeli-e).
# Időbeli élnél a valid_from is az él azonosítója: ugyanaz a tag két időszakban két külön él.
REL_TYPES = {
    "OWNS": ({"Person", "Company"}, {"Company"}, True),
    "OFFICER_OF": ({"Person"}, {"Company"}, True),
    "WORKS_FOR": ({"Person"}, {"Company"}, False),
    "REGISTERED_AT": ({"Company"}, {"Address"}, False),
    "HAS_SITE": ({"Company"}, {"Address"}, False),
    "SEAT_PROVIDER_FOR": ({"Company"}, {"Company"}, False),
    "HAS_ACTIVITY": ({"Company"}, {"Activity"}, False),
    "HAS_ACCOUNT": ({"Company"}, {"BankAccount"}, False),
    "MEMBER_OF": ({"Company"}, {"VatGroup"}, True),
    "PARTY_TO": ({"Company"}, {"Contract"}, False),
    "FOR_PROJECT": ({"Contract"}, {"Project"}, False),
    "ISSUED": ({"Company"}, {"Invoice"}, False),
    "BILLED_TO": ({"Invoice"}, {"Company"}, False),
    "UNDER_CONTRACT": ({"Invoice"}, {"Contract"}, False),
    "AGAINST": ({"InsolvencyProceeding"}, {"Company"}, False),
    "LIQUIDATOR_OF": ({"Company"}, {"InsolvencyProceeding"}, False),
    "FILED_CLAIM": ({"Company"}, {"InsolvencyProceeding"}, False),
    "REPORTED": ({"Company"}, {"Financials"}, False),
}

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

Node = tuple[str, dict]  # (címke, tulajdonságok — benne a kulcs)
Rel = tuple[str, str, str, dict]  # (kezdő kulcs, éltípus, vég kulcs, tulajdonságok)


def get_driver() -> Driver:
    driver = GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))
    driver.verify_connectivity()
    return driver


def ensure_constraints(driver: Driver) -> None:
    for label, key in NODE_KEYS.items():
        # a címke és a kulcs a fenti fix szótárból jön, nem adatból
        driver.execute_query(
            f"CREATE CONSTRAINT {label.lower()}_{key} IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.{key} IS UNIQUE",
            database_=config.NEO4J_DATABASE,
        )


def to_neo4j(value):
    """Az ISO dátum-stringből Neo4j date lesz, így a dátumokra lehet szűrni és rendezni."""
    if isinstance(value, str) and ISO_DATE.match(value):
        return date.fromisoformat(value)
    if isinstance(value, list):
        return [to_neo4j(v) for v in value]
    return value


def clean(props: dict) -> dict:
    # a Neo4j nem tárol null-t; a hiányzó érték egyszerűen nincs ott
    return {k: to_neo4j(v) for k, v in props.items() if v is not None}


def validate(nodes: list[Node], rels: list[Rel]) -> dict[str, str]:
    """Sémaellenőrzés; visszaadja a kulcs → címke indexet, amiből az élek végpontjai jönnek."""
    labels: dict[str, str] = {}
    for label, props in nodes:
        if label not in NODE_KEYS:
            raise ValueError(f"ismeretlen címke: {label}")
        key = props.get(NODE_KEYS[label])
        if key is None:
            raise ValueError(f"{label} kulcs ({NODE_KEYS[label]}) nélkül: {props}")
        if labels.setdefault(key, label) != label:
            raise ValueError(f"a(z) {key} kulcs két címkén is szerepel")
    for start, rtype, end, props in rels:
        if rtype not in REL_TYPES:
            raise ValueError(f"ismeretlen éltípus: {rtype}")
        starts, ends, temporal = REL_TYPES[rtype]
        if labels.get(start) not in starts or labels.get(end) not in ends:
            raise ValueError(
                f"sémasértő él: ({start}:{labels.get(start)})-[:{rtype}]->({end}:{labels.get(end)})"
            )
        if temporal and not props.get("valid_from"):
            raise ValueError(f"az időbeli {rtype} élhez valid_from kell: {start} → {end}")
    return labels


def _write(
    tx: ManagedTransaction, nodes: list[Node], rels: list[Rel], labels: dict, dataset: str
) -> dict:
    node_ids, rel_ids = [], []
    by_label = defaultdict(list)
    for label, props in nodes:
        key = NODE_KEYS[label]
        by_label[label].append({"key": props[key], "props": clean({**props, "dataset": dataset})})
    for label, rows in by_label.items():
        result = tx.run(
            f"UNWIND $rows AS row MERGE (n:{label} {{{NODE_KEYS[label]}: row.key}}) "
            "SET n += row.props RETURN elementId(n) AS id",
            rows=rows,
        )
        node_ids += [r["id"] for r in result]

    by_shape = defaultdict(list)
    for start, rtype, end, props in rels:
        by_shape[(labels[start], rtype, labels[end])].append(
            {"start": start, "end": end, "props": clean({**props, "dataset": dataset})}
        )
    for (start_label, rtype, end_label), rows in by_shape.items():
        identity = "{valid_from: row.props.valid_from}" if REL_TYPES[rtype][2] else ""
        result = tx.run(
            f"UNWIND $rows AS row "
            f"MATCH (a:{start_label} {{{NODE_KEYS[start_label]}: row.start}}) "
            f"MATCH (b:{end_label} {{{NODE_KEYS[end_label]}: row.end}}) "
            f"MERGE (a)-[r:{rtype} {identity}]->(b) "
            "SET r += row.props RETURN elementId(r) AS id",
            rows=rows,
        )
        ids = [r["id"] for r in result]
        if len(ids) != len(rows):
            raise RuntimeError(f"{rtype}: {len(rows)} élből {len(ids)} íródott ki")
        rel_ids += ids

    # szinkron: ami a dataset-ből a forrásban már nincs benne, az a gráfból is törlődik
    removed_rels = tx.run(
        "MATCH ()-[r]->() WHERE r.dataset = $dataset AND NOT elementId(r) IN $ids "
        "DELETE r RETURN count(*) AS n",
        dataset=dataset,
        ids=rel_ids,
    ).single()["n"]
    removed_nodes = tx.run(
        "MATCH (n) WHERE n.dataset = $dataset AND NOT elementId(n) IN $ids "
        "DETACH DELETE n RETURN count(*) AS n",
        dataset=dataset,
        ids=node_ids,
    ).single()["n"]
    return {
        "nodes": len(node_ids),
        "rels": len(rel_ids),
        "removed_nodes": removed_nodes,
        "removed_rels": removed_rels,
    }


def merge_graph(driver: Driver, nodes: list[Node], rels: list[Rel], dataset: str) -> dict:
    """Csomópontok és élek MERGE-ölése egy tranzakcióban; újrafuttatva nem duplikál.

    A `dataset` tulajdonság választja el a forrásokat (seed, később a kinyert korpusz), és
    ez alapján törlődik az is, ami a forrásból kikerült.
    """
    labels = validate(nodes, rels)
    with driver.session(database=config.NEO4J_DATABASE) as session:
        return session.execute_write(_write, nodes, rels, labels, dataset)


def count_graph(driver: Driver) -> dict:
    records, _, _ = driver.execute_query(
        "CALL () { MATCH (n) RETURN count(n) AS nodes } "
        "CALL () { MATCH ()-[r]->() RETURN count(r) AS rels } RETURN nodes, rels",
        database_=config.NEO4J_DATABASE,
    )
    return dict(records[0])
