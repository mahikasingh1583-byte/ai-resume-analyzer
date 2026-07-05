"""
config.py — single source of truth for feature flags & settings.

INTEGRATION ROADMAP
───────────────────
Phase 1  ✅  Clean architecture + Claude/OpenAI API (ship this)
Phase 2  🔜  Firecrawl  → set USE_FIRECRAWL = True, add FIRECRAWL_API_KEY
Phase 3  🔜  RAG        → set USE_RAG = True, run: python rag/build_corpus.py
Phase 4  🔜  CrewAI     → set USE_CREW = True
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── App meta ─────────────────────────────────────────────────────────────────
APP_TITLE = "AI Resume Analyzer"
APP_ICON  = "🚀"

# ── LLM backend ──────────────────────────────────────────────────────────────
# Supported: "anthropic" | "openai" | "ollama"
LLM_BACKEND = os.getenv("LLM_BACKEND", "openai")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL   = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Default model per backend
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-6",
    "openai":    "llama-3.1-8b-instant",
    "ollama":    "qwen3:4b",
}

# ── Phase flags ───────────────────────────────────────────────────────────────
# Flip these to True as you complete each phase.

# Phase 2 — Firecrawl (scrape job URLs instead of manual paste)
USE_FIRECRAWL    = os.getenv("USE_FIRECRAWL", "false").lower() == "true"
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

# Phase 3 — RAG (vector store grounds analysis in real market data)
USE_RAG          = os.getenv("USE_RAG", "false").lower() == "true"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL  = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
RAG_TOP_K        = int(os.getenv("RAG_TOP_K", "5"))

# Phase 4 — CrewAI (multi-agent pipeline)
USE_CREW         = os.getenv("USE_CREW", "false").lower() == "true"
CREW_VERBOSE     = os.getenv("CREW_VERBOSE", "false").lower() == "true"
