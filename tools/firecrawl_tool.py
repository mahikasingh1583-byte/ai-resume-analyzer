"""
tools/firecrawl_tool.py — Phase 2: scrape live job descriptions from URLs.

Usage:
    from tools.firecrawl_tool import scrape_job_url, is_available
    if is_available():
        jd_text = scrape_job_url("https://www.linkedin.com/jobs/view/...")

To activate:
    1. pip install firecrawl-py
    2. Set FIRECRAWL_API_KEY in your .env
    3. Set USE_FIRECRAWL=true in .env (or config.py)
"""

from __future__ import annotations
from config import USE_FIRECRAWL, FIRECRAWL_API_KEY


def is_available() -> bool:
    """Returns True when Firecrawl is configured and enabled."""
    return USE_FIRECRAWL and bool(FIRECRAWL_API_KEY)


def scrape_job_url(url: str) -> str:
    """
    Scrape a job posting URL and return clean markdown text.

    Raises:
        RuntimeError: if Firecrawl is not configured.
        Exception:    if the scrape fails (network, auth, etc.).
    """
    if not is_available():
        raise RuntimeError(
            "Firecrawl is not enabled. Set USE_FIRECRAWL=true and FIRECRAWL_API_KEY in .env"
        )

    from firecrawl import FirecrawlApp

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    result = app.scrape_url(
        url,
        params={
            "formats": ["markdown"],
            "onlyMainContent": True,   # strips nav, footer, ads
        },
    )

    raw = result.get("markdown", "")
    if not raw.strip():
        raise ValueError(f"Firecrawl returned empty content for: {url}")

    return _clean_jd(raw)


def scrape_many_for_corpus(urls: list[str]) -> list[str]:
    """
    Scrape multiple job URLs for building the RAG corpus.
    Skips failures silently so one bad URL doesn't abort the whole build.

    Returns:
        List of successfully scraped markdown strings.
    """
    if not is_available():
        raise RuntimeError("Firecrawl not configured.")

    from firecrawl import FirecrawlApp
    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    results = []
    for url in urls:
        try:
            r = app.scrape_url(url, params={"formats": ["markdown"], "onlyMainContent": True})
            md = r.get("markdown", "").strip()
            if md:
                results.append(_clean_jd(md))
        except Exception as e:
            print(f"[Firecrawl] skipping {url}: {e}")

    return results


def _clean_jd(raw: str) -> str:
    """Strip common boilerplate patterns from scraped job pages."""
    import re
    # Remove markdown links
    raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
    # Collapse excessive blank lines
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()
