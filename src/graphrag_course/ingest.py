"""Betöltési pipeline: Markdown-korpusz → chunkok forrás-metaadattal → embedding → Qdrant."""

import re
import uuid

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models

from graphrag_course import config
from graphrag_course.models import get_embeddings

HEADING = re.compile(r"^(#{1,2}) (.+)$", re.MULTILINE)


def load_documents() -> list[Document]:
    loader = DirectoryLoader(
        str(config.CORPUS_DIR),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = sorted(loader.load(), key=lambda d: d.metadata["source"])
    for doc in docs:
        title = HEADING.search(doc.page_content)
        doc.metadata["doc_id"] = doc.metadata["source"].rsplit("/", 1)[-1].removesuffix(".md")
        doc.metadata["title"] = title.group(2) if title else doc.metadata["doc_id"]
    return docs


def section_span(text: str, start: int, end: int) -> str:
    """A chunk által lefedett ## szakaszok (provenance): „Első” vagy „Első … Utolsó”."""
    # a címsor kezdőpozíciója számít (az endpos a teljes találatot vágná, nem a kezdetét)
    headings = [(m.start(), m.group(2)) for m in HEADING.finditer(text) if m.group(1) == "##"]
    before = [name for pos, name in headings if pos <= start]
    inside = [name for pos, name in headings if start < pos < end]
    first = before[-1] if before else (inside.pop(0) if inside else "(bevezető)")
    return f"{first} … {inside[-1]}" if inside else first


def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        # előbb szakaszhatáron, aztán bekezdésen, soron, mondaton vág
        separators=["\n## ", "\n\n", "\n", ". ", " "],
        add_start_index=True,
    )
    chunks = []
    for doc in docs:
        for i, chunk in enumerate(splitter.split_documents([doc])):
            meta = chunk.metadata
            start = meta["start_index"]
            meta["section"] = section_span(doc.page_content, start, start + len(chunk.page_content))
            meta["chunk_id"] = f"{meta['doc_id']}#{i:02d}"
            # a cím minden chunkba bekerül, különben egy „## Tagok” szakaszról nem derülne ki,
            # melyik cégről szól
            chunk.page_content = f"Dokumentum: {meta['title']}\n\n{chunk.page_content.strip()}"
            chunks.append(chunk)
    return chunks


def recreate_collection(client: QdrantClient) -> None:
    if client.collection_exists(config.COLLECTION):
        client.delete_collection(config.COLLECTION)
    client.create_collection(
        collection_name=config.COLLECTION,
        vectors_config=models.VectorParams(
            size=config.EMBEDDING_DIMENSION, distance=models.Distance.COSINE
        ),
    )


def main() -> None:
    docs = load_documents()
    chunks = split_documents(docs)
    client = QdrantClient(url=config.QDRANT_URL)
    recreate_collection(client)
    store = QdrantVectorStore(
        client=client, collection_name=config.COLLECTION, embedding=get_embeddings()
    )
    # determinisztikus id: újrafuttatáskor ugyanaz a chunk ugyanazt a pontot kapja
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, c.metadata["chunk_id"])) for c in chunks]
    store.add_documents(chunks, ids=ids)
    sizes = sorted(len(c.page_content) for c in chunks)
    print(
        f"{len(docs)} dokumentum → {len(chunks)} chunk "
        f"(méret medián {sizes[len(sizes) // 2]}, max {sizes[-1]} karakter) → '{config.COLLECTION}'"
    )
