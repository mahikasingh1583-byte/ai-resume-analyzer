"""ui/sidebar.py — settings sidebar."""

import streamlit as st
from config import LLM_BACKEND, USE_FIRECRAWL, USE_RAG, USE_CREW


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        st.session_state.dark_mode = st.toggle(
            "🌙 Dark Mode", value=st.session_state.dark_mode
        )

        st.markdown("---")
        st.markdown("## 🤖 AI Backend")
        st.caption(f"Active: **{LLM_BACKEND.upper()}**")

        st.markdown("---")
        st.markdown("## 🕘 Analysis History")

        if st.session_state.history:
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
