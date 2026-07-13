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
        st.divider()

    # ── Cover Letter Generator ────────────────────────────────────────────
    st.subheader("📝 Cover Letter Generator")
    st.caption("Generate a tailored cover letter based on your resume and the job description")

    jd_for_cover = st.session_state.get("last_job_description", "")
    if not jd_for_cover:
        st.info("Run an analysis first — the cover letter uses your resume and the job description.")
    else:
        cover_tone = st.selectbox(
            "Cover letter tone",
            ["Professional & Formal", "Confident & Direct", "Enthusiastic & Modern"],
            key="cover_letter_tone",
        )

        if st.button("✉️ Generate Cover Letter", use_container_width=True):
            tone_map = {
                "Professional & Formal": "formal and polished corporate tone",
                "Confident & Direct": "confident, direct, achievement-focused tone",
                "Enthusiastic & Modern": "enthusiastic, modern, slightly conversational tone"
            }
            prompt = f"""Write a tailored cover letter for this candidate applying to this job.

Resume:
{st.session_state.get('resume_text', '')[:1500]}

Job Description:
{jd_for_cover[:1000]}

Rules:
- Use a {tone_map[cover_tone]}
- Reference specific skills and experience from the resume
- Address specific requirements from the job description
- Keep it to 3-4 paragraphs
- Never invent experience not in the resume
- Start with a strong opening, not "I am writing to apply"
- End with a confident call to action"""

            with st.spinner("Generating your cover letter …"):
                cover_letter = ask_llm(prompt, max_tokens=600)
                st.session_state.cover_letter = cover_letter

        if st.session_state.get("cover_letter"):
            st.markdown(st.session_state.cover_letter)
            st.download_button(
                "📥 Download Cover Letter",
                st.session_state.cover_letter,
                "cover_letter.txt",
                "text/plain",
                use_container_width=True
            )