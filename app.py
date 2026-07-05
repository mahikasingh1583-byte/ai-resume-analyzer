"""
AI Resume Analyzer — Unified App
─────────────────────────────────
PHASE 1 (current): Claude/OpenAI API + clean architecture
PHASE 2 (add Firecrawl): uncomment firecrawl block in ui/tab_analysis.py
PHASE 3 (add RAG):       run python rag/build_corpus.py, toggle USE_RAG=True in config.py
PHASE 4 (add CrewAI):    toggle USE_CREW=True in config.py
"""

import streamlit as st
from config import APP_TITLE, APP_ICON

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# ── Session state bootstrap ──────────────────────────────────────────────────
_defaults = {
    "history": [],
    "mentor_chat": [],
    "dark_mode": False,
    "roadmaps": {},
    "rewritten_resume": "",
    "resume_text": "",
    "last_analysis_result": None,
    "last_job_description": "",
    "jd_source": "paste",   # "paste" | "url" (Phase 2)
}
for k, v in _defaults.items():
    st.session_state.setdefault(k, v)

# ── Theme ────────────────────────────────────────────────────────────────────
from ui.theme import apply_theme, theme_vars
apply_theme(st.session_state.dark_mode)
tv = theme_vars(st.session_state.dark_mode)

# ── Sidebar ──────────────────────────────────────────────────────────────────
from ui.sidebar import render_sidebar
render_sidebar()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="title">🚀 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Upload your resume · paste (or scrape) a job description · get deep AI analysis</div>',
    unsafe_allow_html=True,
)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Analysis",
    "🎓 Career Mentor",
    "✍ Rewriter",
    "📚 Roadmap",
])

from ui.tab_analysis  import render as render_analysis
from ui.tab_mentor    import render as render_mentor
from ui.tab_rewriter  import render as render_rewriter
from ui.tab_roadmap   import render as render_roadmap

with tab1: render_analysis(tv)
with tab2: render_mentor()
with tab3: render_rewriter()
with tab4: render_roadmap()
