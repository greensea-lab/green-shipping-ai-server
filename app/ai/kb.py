from __future__ import annotations

import os
from typing import List, Optional, Tuple

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

from app.config import settings


def _read_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".md", ".txt"}:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".pdf":
        text_parts = []
        reader = PdfReader(path)
        for page in reader.pages:
            try:
                text_parts.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(text_parts)
    return ""


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        j = min(n, i + chunk_size)
        chunk = text[i:j]
        if chunk.strip():
            chunks.append(chunk)
        i = j - overlap
        if i < 0:
            i = 0
    return chunks


def _get_collection():
    os.makedirs(settings.rag_persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=settings.rag_persist_dir)
    # Prefer OpenAI embeddings; fallback to sentence-transformers if no key
    if settings.openai_api_key:
        embed = embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model,
        )
    else:
        # Local embedding to allow offline testing (downloads model on first use)
        try:
            embed = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception:
            # Last resort: DefaultEmbeddingFunction (very basic)
            embed = embedding_functions.DefaultEmbeddingFunction()
    col = client.get_or_create_collection("knowledge_base", embedding_function=embed)
    return col


def ingest_kb(paths: Optional[List[str]] = None) -> int:
    """Ingest files into vector store. Returns number of chunks added.

    If paths is None, scans the default `kb/` directory.
    """
    if paths is None:
        base = os.path.abspath(os.path.join(os.getcwd(), "kb"))
        if not os.path.isdir(base):
            return 0
        # Consider only certain file types
        paths = [
            os.path.join(base, p)
            for p in os.listdir(base)
            if os.path.splitext(p)[1].lower() in {".pdf", ".md", ".txt"}
        ]

    col = _get_collection()
    added = 0
    for p in paths:
        if not os.path.isfile(p):
            continue
        try:
            text = _read_text_from_file(p)
        except Exception:
            continue
        if not text:
            continue
        chunks = _chunk_text(text)
        if not chunks:
            continue
        # Use simple IDs based on filename and index
        fname = os.path.basename(p)
        ids = [f"{fname}:{i}" for i in range(len(chunks))]
        metadatas = [{"source": fname, "path": p} for _ in chunks]
        col.add(ids=ids, documents=chunks, metadatas=metadatas)
        added += len(chunks)
    return added


def search_kb(query: str, top_k: int = 3) -> List[dict]:
    col = _get_collection()
    if not query.strip():
        return []
    try:
        res = col.query(query_texts=[query], n_results=top_k)
    except Exception:
        return []
    out: List[dict] = []
    ids = res.get("ids", [[]])[0]
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    for i, d, m in zip(ids, docs, metas):
        out.append({
            "id": i,
            "snippet": (d[:400] + "…") if d and len(d) > 400 else d,
            "source": (m or {}).get("source"),
            "path": (m or {}).get("path"),
        })
    return out
