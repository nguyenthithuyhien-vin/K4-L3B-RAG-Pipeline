"""
Task 5 — Semantic search.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if top_k <= 0:
        return []
    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    ids = (response.get("ids") or [[]])[0]
    documents = (response.get("documents") or [[]])[0]
    metadatas = (response.get("metadatas") or [[]])[0]
    distances = (response.get("distances") or [[]])[0]

    results = []
    for item_id, content, metadata, distance in zip(
        ids, documents, metadatas, distances
    ):
        meta = dict(metadata or {})
        if meta.get("url") == "":
            meta["url"] = None
        if "chunk_index" in meta:
            meta["chunk_index"] = int(meta["chunk_index"])
        results.append(
            {
                "id": item_id,
                "content": content,
                "score": max(0.0, 1.0 - float(distance)),
                "metadata": meta,
                "retrieval_method": "dense",
            }
        )
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in semantic_search("chỉ tiêu tuyển sinh", top_k=3):
        print(result)
