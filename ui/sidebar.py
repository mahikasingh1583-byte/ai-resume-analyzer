"""ui/sidebar.py — settings sidebar with theme selector + custom color picker."""

import streamlit as st
from config import LLM_BACKEND, USE_FIRECRAWL, USE_RAG, USE_CREW

THEMES = {
    "🌸 Soft Purple (Default)": {
        "bg":     "linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 50%, #C7D2FE 100%)",
        "card":   "rgba(255,255,255,0.85)",
        "text":   "#1F2937",
        "title":  "#4338CA",
        "border": "rgba(99,102,241,0.25)",
        "dark_bg":     "linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #312E81 100%)",
        "dark_card":   "rgba(30,27,75,0.85)",
        "dark_text":   "#F1F5F9",
        "dark_title":  "#A5B4FC",
        "dark_border": "rgba(165,180,252,0.3)",
    },
    "🌊 Ocean Blue": {
        "bg":     "linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 50%, #BFDBFE 100%)",
        "card":   "rgba(255,255,255,0.85)",
        "text":   "#1E3A5F",
        "title":  "#1D4ED8",
        "border": "rgba(59,130,246,0.25)",
        "dark_bg":     "linear-gradient(135deg, #0C1A2E 0%, #0F2847 50%, #1E3A5F 100%)",
        "dark_card":   "rgba(15,40,71,0.85)",
        "dark_text":   "#E0F2FE",
        "dark_title":  "#60A5FA",
        "dark_border": "rgba(96,165,250,0.3)",
    },
    "🌿 Forest Green": {
        "bg":     "linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 50%, #A7F3D0 100%)",
        "card":   "rgba(255,255,255,0.85)",
        "text":   "#064E3B",
        "title":  "#059669",
        "border": "rgba(16,185,129,0.25)",
        "dark_bg":     "linear-gradient(135deg, #022C22 0%, #064E3B 50%, #065F46 100%)",
        "dark_card":   "rgba(6,78,59,0.85)",
        "dark_text":   "#D1FAE5",
        "dark_title":  "#34D399",
        "dark_border": "rgba(52,211,153,0.3)",
    },
    "🌅 Sunset Orange": {
        "bg":     "linear-gradient(135deg, #FFF7ED 0%, #FED7AA 50%, #FDBA74 100%)",
        "card":   "rgba(255,255,255,0.85)",
        "text":   "#7C2D12",
        "title":  "#EA580C",
        "border": "rgba(249,115,22,0.25)",
        "dark_bg":     "linear-gradient(135deg, #1C0A00 0%, #431407 50%, #7C2D12 100%)",
        "dark_card":   "rgba(67,20,7,0.85)",
        "dark_text":   "#FED7AA",
        "dark_title":  "#FB923C",
        "dark_border": "rgba(251,146,60,0.3)",
    },
    "🌙 Midnight Black": {
        "bg":     "linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 50%, #E5E7EB 100%)",
        "card":   "rgba(255,255,255,0.85)",
        "text":   "#111827",
        "title":  "#374151",
        "border": "rgba(107,114,128,0.25)",
        "dark_bg":     "linear-gradient(135deg, #000000 0%, #111827 50%, #1F2937 100%)",
        "dark_card":   "rgba(17,24,39,0.95)",
        "dark_text":   "#F9FAFB",
        "dark_title":  "#D1D5DB",
        "dark_border": "rgba(209,213,219,0.2)",
    },
    "🌺 Rose Pink": {
        "bg":     "linear-gradient(135deg, #FFF1F2 0%, #FFE4E6 50%, #FECDD3 100%)",
        "card":   "rgba(255,255,255,0.85)",
        "text":   "#881337",
        "title":  "#E11D48",
        "border": "rgba(244,63,94,0.25)",
        "dark_bg":     "linear-gradient(135deg, #1A0010 0%, #4C0519 50%, #881337 100%)",
        "dark_card":   "rgba(76,5,25,0.85)",
        "dark_text":   "#FFE4E6",
        "dark_title":  "#FB7185",
        "dark_border": "rgba(251,113,133,0.3)",
    },
}

CUSTOM_LABEL = "🎨 Custom"

_CUSTOM_DEFAULTS = {
    "custom_bg1":    "#EEF2FF",
    "custom_bg2":    "#C7D2FE",
    "custom_card":   "#FFFFFF",
    "custom_text":   "#1F2937",
    "custom_title":  "#4338CA",
    "custom_border": "#6366F1",
}


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _build_custom_theme() -> dict:
    """Build a theme dict on the fly from the color pickers."""
    for k, v in _CUSTOM_DEFAULTS.items():
        st.session_state.setdefault(k, v)

    bg1    = st.session_state.custom_bg1
    bg2    = st.session_state.custom_bg2
    card   = st.session_state.custom_card
    text   = st.session_state.custom_text
    title  = st.session_state.custom_title
    border = st.session_state.custom_border

    return {
        "bg":     f"linear-gradient(135deg, {bg1} 0%, {bg2} 100%)",
        "card":   _hex_to_rgba(card, 0.85),
        "text":   text,
        "title":  title,
        "border": _hex_to_rgba(border, 0.3),
        # dark variants reuse the same custom colors — user controls both directly
        "dark_bg":     f"linear-gradient(135deg, {bg1} 0%, {bg2} 100%)",
        "dark_card":   _hex_to_rgba(card, 0.85),
        "dark_text":   text,
        "dark_title":  title,
        "dark_border": _hex_to_rgba(border, 0.3),
    }


def get_current_theme() -> dict:
    """Return the correct theme vars based on selected theme and dark mode."""
    theme_name = st.session_state.get("selected_theme", "🌸 Soft Purple (Default)")
    dark = st.session_state.get("dark_mode", False)

    if theme_name == CUSTOM_LABEL:
        theme = _build_custom_theme()
    else:
        theme = THEMES.get(theme_name, THEMES["🌸 Soft Purple (Default)"])

    if dark:
        return {
            "bg":     theme["dark_bg"],
            "card":   theme["dark_card"],
            "text":   theme["dark_text"],
            "title":  theme["dark_title"],
            "border": theme["dark_border"],
        }
    return {
        "bg":     theme["bg"],
        "card":   theme["card"],
        "text":   theme["text"],
        "title":  theme["title"],
        "border": theme["border"],
    }


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## ⚙️ Settings")

        # ── Dark mode toggle ──────────────────────────────────────────────────
        st.session_state.dark_mode = st.toggle(
            "🌙 Dark Mode", value=st.session_state.get("dark_mode", False)
        )

        st.markdown("---")

        # ── Theme selector ────────────────────────────────────────────────────
        st.markdown("## 🎨 Theme")
        options = list(THEMES.keys()) + [CUSTOM_LABEL]
        current = st.session_state.get("selected_theme", "🌸 Soft Purple (Default)")
        if current not in options:
            current = "🌸 Soft Purple (Default)"

        selected = st.selectbox(
            "Choose theme",
            options=options,
            index=options.index(current),
            label_visibility="collapsed",
        )
        st.session_state.selected_theme = selected

        # ── Custom color pickers (paint-app style) ──────────────────────────
        if selected == CUSTOM_LABEL:
            for k, v in _CUSTOM_DEFAULTS.items():
                st.session_state.setdefault(k, v)

            c1, c2 = st.columns(2)
            with c1:
                st.session_state.custom_bg1 = st.color_picker(
                    "Background start", st.session_state.custom_bg1
                )
                st.session_state.custom_card = st.color_picker(
                    "Card", st.session_state.custom_card
                )
                st.session_state.custom_title = st.color_picker(
                    "Title / accent", st.session_state.custom_title
                )
            with c2:
                st.session_state.custom_bg2 = st.color_picker(
                    "Background end", st.session_state.custom_bg2
                )
                st.session_state.custom_text = st.color_picker(
                    "Text", st.session_state.custom_text
                )
                st.session_state.custom_border = st.color_picker(
                    "Border", st.session_state.custom_border
                )

        # Show color preview swatches
        tv_preview = get_current_theme()

        st.markdown(
            f"""<div style="
                background:{tv_preview['bg']};
                border-radius:10px;
                padding:10px;
                margin-top:6px;
                text-align:center;
                font-size:12px;
                color:{tv_preview['title']};
                font-weight:600;
                border:1px solid {tv_preview['border']};
            ">Preview: {selected}</div>""",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── History ───────────────────────────────────────────────────────────
        st.markdown("## 🕘 Analysis History")

        if st.session_state.get("history"):
            for item in reversed(st.session_state.history[-5:]):
                st.markdown(
                    f"**{item['filename']}**  \n"
                    f"Score: `{item['score']}%` · {item['time']}"
                )
                st.markdown("---")

            if len(st.session_state.history) > 1:
                st.markdown("### 📈 Score Trend")
                st.line_chart([i["score"] for i in st.session_state.history])

            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        else:
            st.caption("No analyses yet.")
