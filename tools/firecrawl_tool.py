from __future__ import annotations
import re

FIRECRAWL_API_KEY = "fc-df74ee0600e54b23bf69ebe679caaca8"


def is_available() -> bool:
    return bool(FIRECRAWL_API_KEY)


def scrape_job_url(url: str) -> str:
    from firecrawl import FirecrawlApp

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    
    # New Firecrawl API — no params keyword
    result = app.scrape_url(
        url,
        formats=["markdown"],
        only_main_content=True,
    )

    # Handle both old and new response formats
    if hasattr(result, 'markdown'):
        raw = result.markdown or ""
    elif isinstance(result, dict):
        raw = result.get("markdown", "")
    else:
        raw = str(result)

    if not raw.strip():
        raise ValueError(f"Firecrawl returned empty content for: {url}")

    return _clean_jd(raw)


def _clean_jd(raw: str) -> str:
    raw = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()