"""ui/tab_roadmap.py — Tab 4: AI Learning Roadmap (separated from analysis tab)."""

import streamlit as st
from utils.llm_client import ask_llm
from utils.prompts    import roadmap_prompt


def render() -> None:
    st.subheader("📚 AI Learning Roadmap")
    st.caption("Generate a personalised week-by-week plan to close your skill gaps.")

    result = st.session_state.get("last_analysis_result")
    resume = st.session_state.get("resume_text", "")

    if not result:
        st.info("Run an analysis in the Analysis tab first — the roadmap uses your missing skills.")
        return

    missing = result.get("missing", [])
    if missing:
        st.markdown("**Detected skill gaps:** " + ", ".join(f"`{s}`" for s in missing))
    else:
        st.info("No skill gaps detected. The roadmap will focus on deepening your existing strengths.")

    col1, col2 = st.columns([1, 2])
    with col1:
        timeframe = st.selectbox("Roadmap length", ["1 month", "3 months", "6 months"], index=1)
    with col2:
        focus = st.text_input(
            "Optional focus area",
            placeholder="e.g. 'cloud skills', 'machine learning', 'system design'",
        )

    roadmap_key = f"{result['score']}_{timeframe}_{focus}"

    if st.button("🧭 Generate Roadmap", use_container_width=True):
        with st.spinner("Building your personalised roadmap …"):
            prompt = roadmap_prompt(resume, missing, timeframe, focus or "")
            st.session_state.roadmaps[roadmap_key] = ask_llm(prompt, max_tokens=900)

    if roadmap_key in st.session_state.roadmaps:
        st.markdown(st.session_state.roadmaps[roadmap_key])
        st.download_button(
            "📥 Download Roadmap",
            st.session_state.roadmaps[roadmap_key],
            "learning_roadmap.md",
            "text/markdown",
            use_container_width=True,
        )
