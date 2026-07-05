"""
rag/rag_pipeline.py — Phase 3: RAG using ChromaDB + sentence-transformers.

What this does:
    - Embeds job descriptions into a local ChromaDB vector store.
    - At analysis time, retrieves the top-K most similar JDs.
    - That retrieved context is injected into the LLM prompt, grounding
      analysis in real market data rather than one example JD.

To activate:
    1. pip install chromadb sentence-transformers
    2. Run:  python rag/build_corpus.py   (builds the index from scraped JDs)
    3. Set USE_RAG=true in .env
"""

from __future__ import annotations
from config import USE_RAG, CHROMA_PERSIST_DIR, EMBEDDING_MODEL, RAG_TOP_K


def is_available() -> bool:
    """Returns True when RAG is configured and the vector store exists."""
    if not USE_RAG:
        return False
    try:
        import chromadb  # noqa: F401
        from sentence_transformers import SentenceTransformer  # noqa: F401
        return True
    except ImportError:
        return False


def _get_collection():
    """Lazy-load the ChromaDB collection."""
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client.get_or_create_collection("job_descriptions")


def _get_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def retrieve_similar_jds(query_text: str, k: int = RAG_TOP_K) -> list[str]:
    """
    Embed query_text and return the top-k most similar job descriptions
    from the corpus as a list of strings.

    Returns [] when RAG is not available or the corpus is empty.
    """
    if not is_available():
        return []

    collection = _get_collection()
    if collection.count() == 0:
        return []

    embedder = _get_embedder()
    query_embedding = embedder.encode(query_text).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
    )
    return results["documents"][0]  # list[str]


def format_rag_context(similar_jds: list[str]) -> str:
    """Format retrieved JDs into a block for prompt injection."""
    if not similar_jds:
        return ""
    sections = [f"[Similar JD {i+1}]\n{jd[:600]}" for i, jd in enumerate(similar_jds)]
    return "\n\n".join(sections)


def add_documents(texts: list[str], ids: list[str] | None = None) -> None:
    """
    Add job description texts to the vector store.
    Called by rag/build_corpus.py — not used during normal app operation.
    """
    if not texts:
        return

    embedder   = _get_embedder()
    collection = _get_collection()
    embeddings = embedder.encode(texts).tolist()

    if ids is None:
        existing = collection.count()
        ids = [f"jd_{existing + i}" for i in range(len(texts))]

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
    )
    print(f"[RAG] added {len(texts)} documents. Total: {collection.count()}")
