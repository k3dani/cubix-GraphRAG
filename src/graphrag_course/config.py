"""Beállítások a .env-ből; bármilyen OpenAI-kompatibilis végpont megadható."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = PROJECT_ROOT / "corpus"
BASELINE_DIR = PROJECT_ROOT / "baseline"
QUESTIONS_FILE = PROJECT_ROOT / "questions.md"
QUERIES_DIR = PROJECT_ROOT / "queries"

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen36")
LLM_API_KEY = os.getenv("LLM_API_KEY", "not-needed")
# Qwen3-specifikus kapcsoló; más modellnél hagyd üresen
LLM_DISABLE_THINKING = os.getenv("LLM_DISABLE_THINKING", "true").lower() == "true"

EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:8001/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "not-needed")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "naive_rag")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "graphrag-course")
# a Community kiadásban egyetlen felhasználói adatbázis van
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Indoklás: README „Chunkolás” szakasz
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K = int(os.getenv("TOP_K", "4"))
