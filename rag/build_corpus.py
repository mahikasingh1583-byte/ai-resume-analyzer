"""
rag/build_corpus.py — Run this ONCE to build the RAG vector store.

Usage:
    python rag/build_corpus.py

What it does:
    1. Reads job description URLs from rag/jd_urls.txt (one URL per line)
       OR loads local .txt files from rag/sample_jds/
    2. Scrapes each URL with Firecrawl (if enabled) or reads local files
    3. Chunks and embeds them into ChromaDB

You only need to re-run this when you want to refresh the corpus.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
from rag.rag_pipeline import add_documents


def load_local_jds(folder: str = "rag/sample_jds") -> list[str]:
    """Load .txt job description files from a local folder."""
    p = Path(folder)
    if not p.exists():
        return []
    texts = []
    for f in p.glob("*.txt"):
        content = f.read_text(encoding="utf-8").strip()
        if content:
            texts.append(content)
    print(f"[Corpus] loaded {len(texts)} local JDs from {folder}/")
    return texts


def load_from_urls(url_file: str = "rag/jd_urls.txt") -> list[str]:
    """Scrape URLs listed in a text file (one URL per line)."""
    p = Path(url_file)
    if not p.exists():
        print(f"[Corpus] {url_file} not found — skipping URL scraping.")
        return []

    urls = [line.strip() for line in p.read_text().splitlines() if line.strip()]
    print(f"[Corpus] scraping {len(urls)} URLs with Firecrawl …")

    from tools.firecrawl_tool import scrape_many_for_corpus, is_available
    if not is_available():
        print("[Corpus] Firecrawl not configured — skipping URL scraping.")
        return []

    scraped = scrape_many_for_corpus(urls)
    print(f"[Corpus] successfully scraped {len(scraped)} / {len(urls)} URLs")
    return scraped


if __name__ == "__main__":
    all_jds = load_local_jds() + load_from_urls()

    if not all_jds:
        print(
            "\n[Corpus] No job descriptions found!\n"
            "Add .txt files to rag/sample_jds/  OR\n"
            "Add URLs to rag/jd_urls.txt  (requires Firecrawl)\n"
        )
        sys.exit(1)

    print(f"[Corpus] embedding {len(all_jds)} documents …")
    add_documents(all_jds)
    print("[Corpus] Done! Vector store is ready.")
