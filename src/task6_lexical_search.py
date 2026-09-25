"""
Task 6 — Lexical search bằng BM25.
"""

from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from .task4_chunking_indexing import chunk_documents, load_documents


CORPUS: list[dict] = []


def _ensure_corpus() -> None:
    global CORPUS
    if CORPUS:
        return
    standardized = Path(__file__).parent.parent / "data" / "standardized"
    if standardized.exists() and any(standardized.rglob("*.md")):
        CORPUS[:] = chunk_documents(load_documents())


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    _ensure_corpus()
    if not CORPUS or top_k <= 0:
        return []
    tokens = query.lower().split()
    bm25 = build_bm25_index(CORPUS)
    scores = np.asarray(bm25.get_scores(tokens), dtype=float)
    # Okapi IDF = 0 when df == N/2 (common in tiny corpora). Add token-overlap
    # so exact keyword matches still rank above unrelated docs.
    query_set = set(tokens)
    overlap = np.array(
        [
            sum(1 for token in query_set if token in item["content"].lower().split())
            for item in CORPUS
        ],
        dtype=float,
    )
    scores = scores + overlap
    indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for index in indices:
        if scores[index] <= 0:
            continue
        item = CORPUS[index]
        results.append(
            {
                "id": item["id"],
                "content": item["content"],
                "score": float(scores[index]),
                "metadata": item["metadata"],
                "retrieval_method": "bm25",
            }
        )
    return results


if __name__ == "__main__":
    for result in lexical_search("học phí", top_k=3):
        print(result)
