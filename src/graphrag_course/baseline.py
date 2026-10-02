"""Az összes kérdés lefuttatása; az eredmény javítás nélkül a baseline/ mappába kerül."""

import json
import re
from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo

from graphrag_course import config
from graphrag_course.rag import NaiveRag

ROW = re.compile(r"^\| (Q\d+) \| ([\w-]+) \| (.+?) \|$", re.MULTILINE)


def load_questions() -> list[tuple[str, str, str]]:
    return ROW.findall(config.QUESTIONS_FILE.read_text(encoding="utf-8"))


def main() -> None:
    questions = load_questions()
    rag = NaiveRag()
    run_at = datetime.now(ZoneInfo("Europe/Budapest")).isoformat(timespec="seconds")
    settings = {
        "run_at": run_at,
        "llm": config.LLM_MODEL,
        "embedding": config.EMBEDDING_MODEL,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
        "top_k": config.TOP_K,
        "temperature": 0,
    }
    config.BASELINE_DIR.mkdir(exist_ok=True)
    records = []
    md = [
        "# Naiv RAG baseline — válaszok",
        "",
        "Beállítások: " + ", ".join(f"`{k}={v}`" for k, v in settings.items()),
        "",
    ]
    for qid, qtype, question in questions:
        print(f"{qid} ({qtype}) …", flush=True)
        result = rag.ask(question)
        records.append({"id": qid, "type": qtype, **asdict(result)})
        md += [
            f"## {qid} — {qtype}",
            "",
            f"**Kérdés:** {question}",
            "",
            result.answer,
            "",
            "**Visszakeresett chunkok:**",
            "",
        ]
        md += [f"- `{s['chunk_id']}` ({s['section']}), score {s['score']}" for s in result.sources]
        md.append("")
    (config.BASELINE_DIR / "answers.jsonl").write_text(
        "".join(
            json.dumps({**r, "settings": settings}, ensure_ascii=False) + "\n" for r in records
        ),
        encoding="utf-8",
    )
    (config.BASELINE_DIR / "answers.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(records)} válasz → {config.BASELINE_DIR}/answers.md, answers.jsonl")
