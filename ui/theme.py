"""ui/theme.py — CSS injection driven by the currently selected theme dict."""

import streamlit as st


def apply_theme(tv: dict) -> None:
    """
    tv must contain: bg, card, text, title, border
    (this is what ui.sidebar.get_current_theme() returns)
    """
    dark = st.session_state.get("dark_mode", False)

    # These change based on dark/light mode
    uploader_inner = "#1E1B4B" if dark else "#F8F9FF"
    uploader_btn   = "#2D2B55" if dark else "#F3F4F6"

    st.markdown(
        f"""
<style>
#MainMenu {{visibility:hidden;}} footer {{visibility:hidden;}}

/* ── App background ── */
.stApp {{
    background: {tv["bg"]} !important;
    color: {tv["text"]} !important;
}}
[data-testid="stAppViewContainer"] {{
    background: {tv["bg"]} !important;
}}
[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* ── Title animation ── */
.title {{
    text-align:center;font-size:3rem;font-weight:800;
    color:{tv["title"]};animation:float 3s ease-in-out infinite;margin-bottom:5px;
}}
@keyframes float {{
    0%{{transform:translateY(0)}} 50%{{transform:translateY(-8px)}} 100%{{transform:translateY(0)}}
}}
.subtitle {{
    text-align:center;font-size:1.1rem;
    color:{tv["text"]};opacity:.8;margin-bottom:25px;
}}

/* ── Hero card ── */
.hero-card {{
    background:{tv["card"]};backdrop-filter:blur(15px);border-radius:18px;
    padding:20px;border:1px solid {tv["border"]};height:100%;
}}

/* ── File uploader outer box ── */
div[data-testid="stFileUploader"] {{
    border:2px dashed {tv["title"]} !important;
    border-radius:15px !important;
    padding:15px !important;
    background:{tv["card"]} !important;
    transition:all .3s ease;
}}
div[data-testid="stFileUploader"]:hover {{
    box-shadow:0px 10px 25px {tv["border"]};
}}

/* ── File uploader inner box (the white box) ── */
div[data-testid="stFileUploader"] section {{
    background:{uploader_inner} !important;
    border-radius:10px !important;
    border:none !important;
}}
div[data-testid="stFileUploader"] section > div {{
    background:{uploader_inner} !important;
}}

/* ── Upload button ── */
div[data-testid="stFileUploader"] button {{
    background:{uploader_btn} !important;
    color:{tv["text"]} !important;
    border:1px solid {tv["border"]} !important;
    border-radius:8px !important;
}}

/* ── Upload text (drag & drop, file size, etc) ── */
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] small {{
    color:{tv["text"]} !important;
}}

/* ── Buttons ── */
.stButton button {{
    width:100%;height:3.2rem;border-radius:12px;border:none;
    background:linear-gradient(90deg,{tv["title"]},{tv["border"]});
    color:white !important;font-size:16px;font-weight:bold;transition:.3s;
}}
.stButton button:hover {{
    transform:translateY(-3px);
    box-shadow:0 10px 25px {tv["border"]};
}}
.stDownloadButton button {{width:100%;border-radius:12px;}}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background:{tv["card"]};border-radius:15px;padding:12px;
}}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"] {{
    color:{tv["text"]} !important;
}}

/* ── Skill pills ── */
.skill-pill {{
    display:inline-block;padding:6px 14px;border-radius:20px;
    margin:4px;font-size:13.5px;font-weight:600;
}}

/* ── Phase badges ── */
.phase-badge {{
    display:inline-block;font-size:11px;font-weight:600;
    padding:3px 10px;border-radius:20px;margin-bottom:8px;
}}
.phase-active  {{background:#DCFCE7;color:#15803D;}}
.phase-pending {{background:#FEF3C7;color:#B45309;}}

/* ── All text colors ── */
.stApp p, .stApp span, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
    color:{tv["text"]} !important;
}}

/* Tabs */
[data-testid="stTabs"] button p {{
    color:{tv["text"]} !important;
}}

/* Markdown */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {{
    color:{tv["text"]} !important;
}}

/* Expander */
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {{
    color:{tv["text"]} !important;
}}

/* Caption */
[data-testid="stCaptionContainer"] p {{
    color:{tv["text"]} !important;
    opacity:0.75;
}}

/* ── Text inputs and textareas ── */
textarea, input {{
    color:{tv["text"]} !important;
    background-color:{tv["card"]} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background:{tv["card"]} !important;
}}
[data-testid="stSidebar"] * {{
    color:{tv["text"]} !important;
}}

/* ── Chat input pinned to bottom ── */
div[data-testid="stChatInput"] {{
    position:fixed;bottom:0;left:0;right:0;z-index:999;
    background:{tv["bg"]};padding:10px 20px;
    box-shadow:0 -4px 15px rgba(0,0,0,.08);
}}
.main .block-container {{padding-bottom:100px;}}
</style>""",
        unsafe_allow_html=True,
    )


def gauge_html(score: int, card_bg: str, border_color: str, text_color: str) -> str:
    color = "#22C55E" if score >= 75 else "#F59E0B" if score >= 50 else "#EF4444"
    return f"""
<div style="display:flex;justify-content:center;margin:10px 0 25px;">
  <div style="width:170px;height:170px;border-radius:50%;
       background:conic-gradient({color} {score}%,#E5E7EB {score}% 100%);
       display:flex;align-items:center;justify-content:center;">
    <div style="width:130px;height:130px;border-radius:50%;
         background:{card_bg};backdrop-filter:blur(10px);
         display:flex;flex-direction:column;align-items:center;justify-content:center;
         border:1px solid {border_color};">
      <div style="font-size:32px;font-weight:800;color:{color};">{score}%</div>
      <div style="font-size:12px;color:{text_color};opacity:.8;">ATS Match</div>
    </div>
  </div>
</div>"""


def skill_pills(skills: list[str], bg: str, fg: str) -> str:
    if not skills:
        return '<p style="opacity:.7;">None found.</p>'
    return "<div>" + "".join(
        f'<span class="skill-pill" style="background:{bg};color:{fg};">{s}</span>'
        for s in skills
    ) + "</div>"