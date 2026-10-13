"""Dokumentumgráf: Document → Section → Chunk a valódi korpuszból, extrakció nélkül.

A chunkolás ugyanaz, mint a Qdrant-indexé (ingest.split_documents), így a chunk_id közös kulcs:
egy vektoros találatból a gráfba, egy gráfbeli chunkból a vektor-DB-be lehet lépni.
"""

from langchain_core.documents import Document
from neo4j import ManagedTransaction

from graphrag_course import config
from graphrag_course.graph import count_graph, ensure_constraints, get_driver
from graphrag_course.ingest import HEADING, load_documents, split_documents

# a fájlnév előtagja a dokumentumtípus (a korpusz elnevezési konvenciója)
DOC_TYPES = {
    "cegkivonat": "cégkivonat",
    "szerzodes": "szerződés",
    "level": "levél",
    "email": "e-mail",
    "szamla": "számla",
    "jelentes": "jelentés",
}
PREAMBLE = "(bevezető)"


def sections_of(doc: Document) -> list[dict]:
    """A ## szakaszok karakter-tartománnyal; az első ## előtti rész (cím, fejléc) a 0. szakasz."""
    text = doc.page_content
    starts = [(0, PREAMBLE)] + [
        (m.start(), m.group(2)) for m in HEADING.finditer(text) if m.group(1) == "##"
    ]
    sections = []
    for order, (start, heading) in enumerate(starts):
        end = starts[order + 1][0] if order + 1 < len(starts) else len(text)
        sections.append(
            {
                "section_id": f"{doc.metadata['doc_id']}/{order:02d}",
                "props": {
                    "heading": heading,
                    "order": order,
                    "char_start": start,
                    "char_end": end,
                    "char_count": len(text[start:end].strip()),
                },
            }
        )
    return sections


def build_rows(docs: list[Document], chunks: list[Document]) -> dict:
    by_doc = {d.metadata["doc_id"]: d for d in docs}
    sections = {doc_id: sections_of(d) for doc_id, d in by_doc.items()}
    chunk_rows = []
    for chunk in chunks:
        meta = chunk.metadata
        doc_id, start, end = meta["doc_id"], meta["start_index"], meta["end_index"]
        # a Qdrant-ba a címmel prefixelt szöveg került; a gráfba a nyers, dokumentumbeli szöveg
        text = by_doc[doc_id].page_content[start:end]
        covered = [
            s["section_id"]
            for s in sections[doc_id]
            if start < s["props"]["char_end"] and s["props"]["char_start"] < end
        ]
        chunk_rows.append(
            {
                "chunk_id": meta["chunk_id"],
                "doc_id": doc_id,
                "sections": covered,
                "props": {
                    "doc_id": doc_id,
                    "index": int(meta["chunk_id"].rsplit("#", 1)[1]),
                    "text": text,
                    "char_start": start,
                    "char_end": end,
                    "char_count": len(text),
                    "section": meta["section"],
                },
            }
        )
    chunk_count = {doc_id: 0 for doc_id in by_doc}
    for row in chunk_rows:
        chunk_count[row["doc_id"]] += 1
    doc_rows = [
        {
            "doc_id": doc_id,
            "props": {
                "title": d.metadata["title"],
                # relatív út: a gráfba (és a publikus kimenetekbe) ne kerüljön lokális útvonal
                "source": f"{config.CORPUS_DIR.name}/{doc_id}.md",
                "doc_type": DOC_TYPES.get(doc_id.split("_", 1)[0], "egyéb"),
                "char_count": len(d.page_content),
                "chunk_count": chunk_count[doc_id],
                "section_count": len(sections[doc_id]),
            },
        }
        for doc_id, d in by_doc.items()
    ]
    section_rows = [{**s, "doc_id": doc_id} for doc_id, ss in sections.items() for s in ss]

    def chain(rows: list[dict], key: str) -> list[list[str]]:
        # egymást követő elemek egy dokumentumon belül (a sorok dokumentumonként rendezettek)
        return [
            [a[key], b[key]]
            for a, b in zip(rows, rows[1:], strict=False)
            if a["doc_id"] == b["doc_id"]
        ]

    return {
        "docs": doc_rows,
        "sections": section_rows,
        "chunks": chunk_rows,
        "next_section": chain(section_rows, "section_id"),
        "next_chunk": chain(chunk_rows, "chunk_id"),
    }


def write(tx: ManagedTransaction, rows: dict) -> None:
    tx.run(
        "UNWIND $rows AS row MERGE (d:Document {doc_id: row.doc_id}) SET d += row.props",
        rows=rows["docs"],
    )
    tx.run(
        "UNWIND $rows AS row "
        "MATCH (d:Document {doc_id: row.doc_id}) "
        "MERGE (s:Section {section_id: row.section_id}) SET s += row.props "
        "MERGE (d)-[:HAS_SECTION]->(s)",
        rows=rows["sections"],
    )
    tx.run(
        "UNWIND $rows AS row "
        "MATCH (d:Document {doc_id: row.doc_id}) "
        "MERGE (c:Chunk {chunk_id: row.chunk_id}) SET c += row.props "
        "MERGE (d)-[:CONTAINS]->(c) "
        "WITH c, row "
        "UNWIND row.sections AS section_id "
        "MATCH (s:Section {section_id: section_id}) "
        "MERGE (c)-[:IN_SECTION]->(s)",
        rows=rows["chunks"],
    )
    for rel, label, key, pairs in (
        ("NEXT_SECTION", "Section", "section_id", rows["next_section"]),
        ("NEXT_CHUNK", "Chunk", "chunk_id", rows["next_chunk"]),
    ):
        tx.run(
            f"UNWIND $pairs AS pair "
            f"MATCH (a:{label} {{{key}: pair[0]}}), (b:{label} {{{key}: pair[1]}}) "
            f"MERGE (a)-[:{rel}]->(b)",
            pairs=pairs,
        )
        # elavult lánc-élek (pl. más chunkméret után)
        tx.run(
            f"MATCH (a:{label})-[r:{rel}]->(b:{label}) "
            f"WHERE NOT [a.{key}, b.{key}] IN $pairs DELETE r",
            pairs=pairs,
        )
    tx.run(
        "UNWIND $rows AS row "
        "MATCH (c:Chunk {chunk_id: row.chunk_id})-[r:IN_SECTION]->(s:Section) "
        "WHERE NOT s.section_id IN row.sections DELETE r",
        rows=rows["chunks"],
    )
    # ami a korpuszból kikerült (vagy más chunkolás után megszűnt), az a gráfból is törlődik;
    # a DETACH a 3. héten a chunkokra akasztott MENTIONS éleket is viszi
    for label, key, ids in (
        ("Chunk", "chunk_id", [r["chunk_id"] for r in rows["chunks"]]),
        ("Section", "section_id", [r["section_id"] for r in rows["sections"]]),
        ("Document", "doc_id", [r["doc_id"] for r in rows["docs"]]),
    ):
        tx.run(f"MATCH (n:{label}) WHERE NOT n.{key} IN $ids DETACH DELETE n", ids=ids)


def main() -> None:
    docs = load_documents()
    chunks = split_documents(docs)
    rows = build_rows(docs, chunks)
    with get_driver() as driver:
        ensure_constraints(driver)
        with driver.session(database=config.NEO4J_DATABASE) as session:
            session.execute_write(write, rows)
        total = count_graph(driver)
    print(
        f"{len(rows['docs'])} dokumentum, {len(rows['sections'])} szakasz, "
        f"{len(rows['chunks'])} chunk → Neo4j "
        f"(a gráf összesen: {total['nodes']} csomópont, {total['rels']} él)"
    )
