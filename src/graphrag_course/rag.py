"""Lekérdező út: kérdés → embedding → top-k keresés → prompt → LLM → válasz forrásokkal."""

import sys
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from graphrag_course import config
from graphrag_course.models import get_embeddings, get_llm

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Céges dokumentumokból válaszolsz magyarul. Kizárólag a megadott kontextusra "
            "támaszkodj. Minden állítás után szögletes zárójelben add meg a forrás chunk "
            "azonosítóját, pl. [cegkivonat_dummy#00]. Ha a kontextus nem elég a válaszhoz, "
            "mondd ki, hogy a rendelkezésre álló dokumentumok alapján nem tudod megválaszolni, "
            "és ne egészítsd ki saját tudásból.",
        ),
        ("human", "Kontextus:\n\n{context}\n\nKérdés: {question}"),
    ]
)


@dataclass
class Answer:
    question: str
    answer: str
    sources: list[dict]


class NaiveRag:
    def __init__(self, top_k: int = config.TOP_K) -> None:
        self.store = QdrantVectorStore(
            client=QdrantClient(url=config.QDRANT_URL),
            collection_name=config.COLLECTION,
            embedding=get_embeddings(),
        )
        self.top_k = top_k
        self.chain = PROMPT | get_llm()

    def retrieve(self, question: str) -> list[tuple[Document, float]]:
        return self.store.similarity_search_with_score(question, k=self.top_k)

    @staticmethod
    def format_context(hits: list[tuple[Document, float]]) -> str:
        return "\n\n---\n\n".join(f"[{d.metadata['chunk_id']}]\n{d.page_content}" for d, _ in hits)

    def ask(self, question: str) -> Answer:
        hits = self.retrieve(question)
        response = self.chain.invoke({"context": self.format_context(hits), "question": question})
        sources = [
            {
                "chunk_id": d.metadata["chunk_id"],
                "source": d.metadata["doc_id"] + ".md",
                "section": d.metadata["section"],
                "score": round(score, 4),
            }
            for d, score in hits
        ]
        return Answer(question=question, answer=str(response.content).strip(), sources=sources)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('Használat: uv run ask "kérdés"')
    result = NaiveRag().ask(" ".join(sys.argv[1:]))
    print(result.answer)
    print("\nFelhasznált chunkok:")
    for s in result.sources:
        print(f"  {s['score']:.3f}  {s['chunk_id']}  ({s['source']} › {s['section']})")
