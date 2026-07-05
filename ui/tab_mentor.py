"""ui/tab_mentor.py — Tab 2: Career Mentor chat."""

import streamlit as st
from utils.llm_client import ask_llm
from utils.prompts    import mentor_system_prompt


def render() -> None:
    st.subheader("🎓 Career Mentor")
    st.caption("Ask career, resume, interview, or skill-development questions.")

    has_resume = bool(st.session_state.get("resume_text"))

    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        personalized = st.toggle(
            "🎯 Personalize using my resume",
            value=has_resume,
            disabled=not has_resume,
        )
        if not has_resume:
            st.caption("Upload a resume in the Analysis tab to unlock personalized mentoring.")
    with top_col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.mentor_chat = []
            st.rerun()

    for msg in st.session_state.mentor_chat:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Ask your mentor …", key="mentor_input")
    if not prompt:
        return

    is_first = len(st.session_state.mentor_chat) == 0
    st.session_state.mentor_chat.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    system = mentor_system_prompt(
        personalized=personalized,
        resume_text=st.session_state.get("resume_text", ""),
        last_result=st.session_state.get("last_analysis_result"),
        full_context=is_first,
    )

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.mentor_chat[:-1]
    ][-6:]

    with st.chat_message("assistant"):
        with st.spinner("Thinking …"):
            answer = ask_llm(prompt, system=system, history=history, max_tokens=500)
        st.write(answer)

    st.session_state.mentor_chat.append({"role": "assistant", "content": answer})
    st.rerun()
