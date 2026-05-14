"""
RAG system for Israeli law retrieval.

Flow:
  1. build_index()  — run once (or via build_law_index.py). Chunks IsraelyLaw.txt,
                      embeds with a multilingual model, persists to .rag_cache/.
  2. query_relevant_laws(query)  — called at session start. Returns the most
                                   semantically relevant law sections for the case.

The index is built once and reused across all sessions.
"""

import os
import re

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ── Paths ─────────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LAW_FILE = os.path.join(_ROOT, "Assets", "IsraelyLaw.txt")
CACHE_DIR = os.path.join(_ROOT, ".rag_cache")

# ── Config ────────────────────────────────────────────────────────────────────
COLLECTION_NAME = "israeli_law"
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # handles Hebrew
CHUNK_SIZE = 900       # characters per chunk — balances context vs retrieval precision
CHUNK_OVERLAP = 150    # overlap keeps context across chunk boundaries
TOP_K = 6              # chunks returned per query — covers enough law without bloating prompt


def _embedding_function():
    return SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)


def _get_client() -> chromadb.PersistentClient:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CACHE_DIR)


def is_index_built() -> bool:
    """Return True if the law index has been built and contains documents."""
    try:
        client = _get_client()
        col = client.get_collection(name=COLLECTION_NAME, embedding_function=_embedding_function())
        return col.count() > 0
    except Exception:
        return False


def _clean_law_text(text: str) -> str:
    """Remove common OCR artifacts from the scanned law file."""
    text = re.sub(r"[¸·]{2,}", "", text)
    text = re.sub(r"‏", "", text)          # Hebrew RTL mark
    text = re.sub(r"\s{3,}", "  ", text)
    text = re.sub(r"-{3,}", "—", text)
    return text.strip()


def _chunk_text(text: str) -> list[dict]:
    """
    Split the law text into overlapping chunks.
    Tries to split on natural section boundaries first (law/section headers),
    then falls back to character-level sliding window.
    """
    text = _clean_law_text(text)
    chunks = []
    chunk_id = 0

    # Split on Hebrew legal section markers to preserve context
    boundary = re.compile(
        r"(?=(?:חוק |פקודת |תקנות |צו |סעיף \d|^\d{1,3}[\.\)]\s))",
        re.MULTILINE,
    )
    sections = [s.strip() for s in boundary.split(text) if len(s.strip()) > 80]

    for section in sections:
        if len(section) <= CHUNK_SIZE:
            chunks.append({"id": str(chunk_id), "text": section})
            chunk_id += 1
        else:
            # Slide a window through long sections
            start = 0
            while start < len(section):
                chunk_text = section[start: start + CHUNK_SIZE].strip()
                if len(chunk_text) > 80:
                    chunks.append({"id": str(chunk_id), "text": chunk_text})
                    chunk_id += 1
                start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def build_index(force_rebuild: bool = False) -> int:
    """
    Build the RAG index from IsraelyLaw.txt and persist it to .rag_cache/.
    Safe to call multiple times — skips if already built unless force_rebuild=True.

    Returns: number of chunks indexed
    """
    client = _get_client()
    ef = _embedding_function()

    if force_rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    if not force_rebuild and is_index_built():
        col = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        return col.count()

    with open(LAW_FILE, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    chunks = _chunk_text(raw)
    col = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)

    # Add in batches to avoid memory spikes
    batch_size = 64
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i: i + batch_size]
        col.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
        )

    return len(chunks)


def query_relevant_laws(query: str, n_results: int = TOP_K) -> str:
    """
    Retrieve the most semantically relevant law sections for a given query.

    Args:
        query: Free-text description of the case (charges, facts, evidence, case type)
        n_results: Number of chunks to return

    Returns:
        Relevant law sections joined as a single string, ready for prompt injection
    """
    if not is_index_built():
        build_index()

    client = _get_client()
    ef = _embedding_function()
    col = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)

    results = col.query(query_texts=[query], n_results=n_results)
    chunks: list[str] = results["documents"][0]

    return "\n\n---\n\n".join(chunks)
