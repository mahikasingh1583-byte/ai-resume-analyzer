"""ui/tab_rewriter.py — Tab 3: AI Resume Rewriter."""

import streamlit as st
from utils.llm_client import ask_llm
from utils.prompts    import rewrite_prompt

TONES = {
    "Professional & Formal":
        "Use a formal, polished, traditional corporate tone.",
    "Concise & Achievement-driven":
        "Be as concise as possible — short, punchy, metric-heavy bullets.",
    "Modern & Conversational":
        "Use a modern, slightly conversational but still professional tone.",
}


def render() -> None:
    st.subheader("✍ AI Resume Rewriter")

    if not st.session_state.get("resume_text"):
        st.info("Upload and analyze a resume in the Analysis tab first.")
        return

    resume_text = st.session_state.resume_text
    st.caption(f"Resume length: {len(resume_text):,} characters")

    tone = st.selectbox("Rewrite tone", list(TONES.keys()))

    if st.button("🚀 Rewrite Resume", use_container_width=True):
        prompt = rewrite_prompt(resume_text, TONES[tone])
        with st.spinner("AI is rewriting your resume …"):
            st.session_state.rewritten_resume = ask_llm(prompt, max_tokens=1200)
        st.success("Resume rewritten!")

    if st.session_state.get("rewritten_resume"):
        st.markdown(st.session_state.rewritten_resume)
        st.download_button(
            "📥 Download Rewritten Resume (.md)",
            st.session_state.rewritten_resume,
            "rewritten_resume.md",
            "text/markdown",
            use_container_width=True,
        )
