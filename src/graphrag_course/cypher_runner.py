"""A queries/*.cypher lekérdezések futtatása; a kimenet a queries/results.md-be kerül.

Fájlformátum: az első `//` sor a cím, a további `//` sorok a leírás, a `// params: {...}` sorok
JSON-paraméterek. A fájl a Neo4j Browserbe is bemásolható (előtte `:params {...}`).
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from neo4j import RoutingControl
from neo4j.time import Date, DateTime

from graphrag_course import config
from graphrag_course.graph import get_driver

PARAMS_PREFIX = "// params:"


def parse(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    comments = [line for line in lines if line.startswith("//")]
    params = {}
    description = []
    for line in comments[1:]:
        if line.startswith(PARAMS_PREFIX):
            # több params-sor is lehet, mindegyik egy teljes JSON-objektum
            params.update(json.loads(line.removeprefix(PARAMS_PREFIX)))
        else:
            description.append(line.removeprefix("//").strip())
    return {
        "name": path.stem,
        "title": comments[0].removeprefix("//").strip(),
        "description": " ".join(description).strip(),
        "params": params,
        "cypher": "\n".join(line for line in lines if not line.startswith("//")).strip(),
    }


def fmt(value) -> str:
    if value is None or value == []:
        return "—"
    if isinstance(value, Date | DateTime):
        return value.iso_format()
    if isinstance(value, bool):
        return "igen" if value else "nem"
    if isinstance(value, float):
        return f"{value:.1f}" if value != int(value) else str(int(value))
    if isinstance(value, list):
        return ", ".join(fmt(v) for v in value)
    # a | a markdown-táblát törné, az újsor a sort
    return str(value).replace("|", "\\|").replace("\n", " ⏎ ")


def to_markdown(keys: list[str], records: list) -> str:
    if not records:
        return "*(nincs találat)*"
    rows = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    rows += ["| " + " | ".join(fmt(r[k]) for k in keys) + " |" for r in records]
    return "\n".join(rows)


def main() -> None:
    only = sys.argv[1:]  # opcionálisan: fájlnév-részletek, pl. `uv run graph-queries 06 07`
    paths = sorted(config.QUERIES_DIR.glob("*.cypher"))
    if only:
        paths = [p for p in paths if any(o in p.stem for o in only)]
    run_at = datetime.now(ZoneInfo("Europe/Budapest")).isoformat(timespec="seconds")
    md = [
        "# Cypher-lekérdezések és kimenetük",
        "",
        f"Futtatva: {run_at}, `uv run graph-queries`. A lekérdezések a `queries/*.cypher` "
        "fájlokban vannak; ez a fájl generált.",
        "",
    ]
    with get_driver() as driver:
        for path in paths:
            q = parse(path)
            records, _, keys = driver.execute_query(
                q["cypher"],
                parameters_=q["params"],
                routing_=RoutingControl.READ,
                database_=config.NEO4J_DATABASE,
            )
            print(f"{q['name']}: {len(records)} sor")
            md += [f"## {q['title']}", "", f"`{path.name}` — {q['description']}", ""]
            if q["params"]:
                md += [f"Paraméterek: `{json.dumps(q['params'], ensure_ascii=False)}`", ""]
            md += ["```cypher", q["cypher"], "```", "", to_markdown(keys, records), ""]
    if only:
        # részleges futás: nem írja felül a results.md-t, a kimenet a képernyőre megy
        print("\n".join(md[4:]))
    else:
        (config.QUERIES_DIR / "results.md").write_text("\n".join(md), encoding="utf-8")
        print(f"{len(paths)} lekérdezés → {config.QUERIES_DIR.name}/results.md")
