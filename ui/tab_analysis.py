"""
ui/tab_analysis.py — Tab 1: Resume Analysis.
Upgraded UI: skill score pills, expandable weakness cards, areas for improvement.
"""

from __future__ import annotations
import os
import streamlit as st
from datetime import datetime

from utils.resume_parser import extract_text, analyze_resume
from utils.prompts       import analysis_prompt
from utils.llm_client    import ask_llm
from ui.theme            import gauge_html, skill_pills
from config              import USE_FIRECRAWL, USE_RAG, USE_CREW


def render(tv: dict) -> None:

    # ── Get usage count ───────────────────────────────────────────────────────
    try:
        from utils.counter import get_count
        total_count = get_count()
        usage_badge = f"🔥 {total_count}+ resumes analyzed" if total_count > 0 else ""
    except Exception:
        usage_badge = ""

    # ── Hero ─────────────────────────────────────────────────────────────────
    hero_col, anim_col = st.columns([2, 1])
    with hero_col:
        st.markdown(
            f'<div class="hero-card">'
            f'<h3 style="margin-top:0;">🎯 Land Your Dream Job Faster</h3>'
            f'<p style="font-size:15.5px;opacity:.9;">'
            f'ATS score · missing skills · line-by-line critique · interview prep — all in one run.'
            f'</p>'
            f'<p style="font-size:13px;opacity:0.7;margin-top:8px;">{usage_badge}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with anim_col:
        _scan_animation(tv)

    st.write("")

    # ── Upload section ────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("📄 Resume")
            resume = st.file_uploader(
                "Upload Resume", type=["pdf", "docx"],
                label_visibility="collapsed"
            )
    with col2:
        with st.container(border=True):
            st.subheader("💼 Job Description")

            # ── PHASE 2: Firecrawl URL input ──────────────────────────────────
            if USE_FIRECRAWL:
                jd_source = st.radio(
                    "Source", ["Paste text", "Scrape URL"],
                    horizontal=True, label_visibility="collapsed",
                )
                if jd_source == "Scrape URL":
                    jd_url = st.text_input(
                        "Job posting URL",
                        placeholder="https://www.linkedin.com/jobs/view/...",
                        label_visibility="collapsed",
                    )
                    job_description = ""
                    if jd_url and st.button("🌐 Fetch JD"):
                        with st.spinner("Scraping with Firecrawl …"):
                            try:
                                from tools.firecrawl_tool import scrape_job_url
                                job_description = scrape_job_url(jd_url)
                                st.session_state.scraped_jd = job_description
                                st.success("✅ Job description fetched!")
                            except Exception as e:
                                st.error(f"Firecrawl error: {e}")
                    job_description = st.session_state.get("scraped_jd", "")
                else:
                    job_description = st.text_area(
                        "Job Description", height=180,
                        placeholder="Paste the job description here …",
                        label_visibility="collapsed",
                    )
            # ── PHASE 1: plain paste ──────────────────────────────────────────
            else:
                job_description = st.text_area(
                    "Job Description", height=180,
                    placeholder="Paste the job description here …",
                    label_visibility="collapsed",
                )

    # ── Resume processing ─────────────────────────────────────────────────────
    if not resume:
        st.info("👆 Upload a PDF or DOCX resume above to get started.")
        return

    with st.spinner("Reading resume …"):
        resume_text = extract_text(resume)
        if resume_text:
            st.session_state.resume_text = resume_text

    if not resume_text.strip():
        st.error("⚠ Couldn't extract text — try a text-based PDF/DOCX.")
        st.stop()

    st.success("✅ Resume uploaded!")

    with st.expander("📄 View extracted text"):
        st.text_area("", resume_text, height=250, label_visibility="collapsed")
        st.download_button(
            "📥 Download text", resume_text,
            "resume_text.txt", "text/plain",
            use_container_width=True
        )

    st.divider()

    if not st.button("🚀 Analyze Resume", use_container_width=True):
        return

    if not job_description.strip():
        st.warning("⚠ Please provide a job description before analyzing.")
        return

    # ── PHASE 3: RAG context retrieval ───────────────────────────────────────
    rag_context = ""
    if USE_RAG:
        with st.spinner("🔍 Retrieving similar roles from market corpus …"):
            try:
                from rag.rag_pipeline import retrieve_similar_jds, format_rag_context

                chroma_found = any(
                    os.path.exists(p) for p in
                    ["./chroma_db", "chroma_db", "../chroma_db"]
                )

                if chroma_found:
                    similar     = retrieve_similar_jds(job_description)
                    rag_context = format_rag_context(similar)
                    if rag_context:
                        st.caption(f"📚 RAG: grounded analysis with {len(similar)} similar JDs.")
                    else:
                        st.caption("📚 RAG: vector store found but no similar JDs returned.")
                else:
                    st.caption("📚 RAG: vector store not found — run `python rag/build_corpus.py` first.")

            except Exception as e:
                st.caption(f"📚 RAG skipped: {e}")

    # ── PHASE 4: CrewAI multi-agent pipeline ─────────────────────────────────
    if USE_CREW:
        with st.spinner("🤖 Running CrewAI pipeline …"):
            try:
                from agents.crew import run_crew_analysis
                crew_result = run_crew_analysis(resume_text, job_description)
                _render_crew_results(crew_result, resume, tv)
                return
            except Exception as e:
                st.warning(f"CrewAI failed ({e}), falling back to single-agent.")

    # ── Single-agent analysis ─────────────────────────────────────────────────
    with st.spinner("Running deep AI analysis …"):
        result   = analyze_resume(resume_text, job_description)
        prompt   = analysis_prompt(
            resume_text, job_description,
            result["matched"], result["missing"], result["score"],
            rag_context=rag_context,
        )
        feedback = ask_llm(prompt, max_tokens=1500)

        skill_scores = _get_skill_scores(resume_text, result["missing"])

    _save_result(resume.name, result, job_description)
    _render_single_results(result, feedback, resume, tv, skill_scores)


# ── Skill scoring ─────────────────────────────────────────────────────────────

def _get_skill_scores(resume_text: str, missing_skills: list) -> dict:
    """Score each missing skill 0-10 based on resume evidence."""
    if not missing_skills:
        return {}

    skills_list = ", ".join(missing_skills[:10])
    prompt = f"""Rate how well this resume demonstrates each skill from 0-10.
0 = not mentioned at all, 10 = strong clear evidence.

Resume:
{resume_text[:1500]}

Skills to rate: {skills_list}

Respond ONLY as comma-separated skill:score pairs like this:
Docker:0, Kubernetes:2, AWS:1, PostgreSQL:3

No extra text."""

    try:
        response = ask_llm(prompt, max_tokens=150)
        scores   = {}
        for item in response.split(","):
            item = item.strip()
            if ":" in item:
                parts = item.split(":")
                skill = parts[0].strip()
                try:
                    score = int("".join(filter(str.isdigit, parts[1])))
                    scores[skill] = max(0, min(10, score))
                except Exception:
                    scores[skill] = 0
        return scores
    except Exception:
        return {skill: 0 for skill in missing_skills}


# ── Save result ───────────────────────────────────────────────────────────────

def _save_result(filename: str, result: dict, jd: str) -> None:
    st.session_state.last_analysis_result = result
    st.session_state.last_job_description = jd
    st.session_state.history.append({
        "filename": filename,
        "score":    result["score"],
        "time":     datetime.now().strftime("%H:%M:%S"),
    })

    # Increment global usage counter
    try:
        from utils.counter import increment_count
        increment_count()
    except Exception:
        # Fallback to file-based counter if Supabase not configured
        try:
            counter_file = "usage_count.txt"
            count = 0
            if os.path.exists(counter_file):
                with open(counter_file, "r") as f:
                    count = int(f.read().strip() or 0)
            count += 1
            with open(counter_file, "w") as f:
                f.write(str(count))
        except Exception:
            pass


# ── Main results renderer ─────────────────────────────────────────────────────

def _render_single_results(
    result: dict, feedback: str, resume, tv: dict, skill_scores: dict
) -> None:
    st.success("🎉 Analysis complete!")

    # ── ATS Score gauge ───────────────────────────────────────────────────────
    st.subheader("📊 ATS Match Score")
    st.markdown(
        gauge_html(result["score"], tv["card"], tv["border"], tv["text"]),
        unsafe_allow_html=True,
    )
    st.progress(result["score"] / 100)

    st.divider()

    # ── Metrics ───────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Skills Matched",      len(result["matched"]))
    c2.metric("⚠ Missing Skills",      len(result["missing"]))
    c3.metric("🎯 Interview Readiness", f"{max(10, min(95, result['score']-5))}%")

    st.divider()

    # ── Matched skills ────────────────────────────────────────────────────────
    if result["matched"]:
        st.subheader("✅ Skills Found")
        _render_matched_pills(result["matched"])

    st.write("")

    # ── Missing skills with scores ────────────────────────────────────────────
    if result["missing"]:
        st.subheader("🚨 Areas for Improvement")
        st.caption("Score shows how much evidence exists in your resume (0 = not mentioned, 10 = strong evidence)")
        _render_scored_pills(result["missing"], skill_scores)

        st.write("")

        st.subheader("📋 Detailed Weakness Analysis")
        _render_weakness_cards(result["missing"], skill_scores)

    st.divider()

    # ── AI feedback ───────────────────────────────────────────────────────────
    st.subheader("🤖 AI Resume Review")
    st.markdown(_format_feedback(feedback))

    st.divider()

    # ── Download report ───────────────────────────────────────────────────────
    report = "\n".join([
        "AI RESUME ANALYZER — REPORT",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"File: {resume.name}",
        f"\nATS Score: {result['score']}%",
        f"\nMatched: {', '.join(result['matched']) or 'None'}",
        f"\nMissing: {', '.join(result['missing']) or 'None'}",
        f"\n\n{feedback}",
    ])
    st.download_button(
        "📥 Download Full Report", report,
        f"analysis_{datetime.now():%Y%m%d_%H%M%S}.txt",
        "text/plain", use_container_width=True,
    )
    st.balloons()


# ── Skill pill renderers ──────────────────────────────────────────────────────

def _render_matched_pills(skills: list) -> None:
    html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;">'
    for skill in skills:
        html += f"""
        <span style="
            background:linear-gradient(135deg,#22C55E,#16A34A);
            color:white;padding:6px 16px;border-radius:20px;
            font-size:13px;font-weight:600;
            box-shadow:0 2px 8px rgba(34,197,94,0.3);
        ">{skill}</span>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _render_scored_pills(skills: list, scores: dict) -> None:
    html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px;">'
    for skill in skills:
        score = scores.get(skill, 0)
        if score <= 2:
            bg     = "linear-gradient(135deg,#EF4444,#DC2626)"
            shadow = "rgba(239,68,68,0.3)"
        elif score <= 5:
            bg     = "linear-gradient(135deg,#F59E0B,#D97706)"
            shadow = "rgba(245,158,11,0.3)"
        else:
            bg     = "linear-gradient(135deg,#6366F1,#4F46E5)"
            shadow = "rgba(99,102,241,0.3)"

        html += f"""
        <span style="
            background:{bg};color:white;
            padding:6px 16px;border-radius:20px;
            font-size:13px;font-weight:600;
            box-shadow:0 2px 8px {shadow};
            display:inline-flex;align-items:center;gap:6px;
        ">
            {skill}
            <span style="
                background:rgba(255,255,255,0.25);
                padding:1px 7px;border-radius:10px;
                font-size:11px;font-weight:700;
            ">{score}/10</span>
        </span>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _render_weakness_cards(skills: list, scores: dict) -> None:
    for skill in skills:
        score = scores.get(skill, 0)
        if score <= 2:
            icon  = "🔴"
            label = "Critical Gap"
        elif score <= 5:
            icon  = "🟡"
            label = "Moderate Gap"
        else:
            icon  = "🔵"
            label = "Minor Gap"

        with st.expander(f"{icon} {skill}  —  Score: {score}/10  ({label})"):
            if score == 0:
                st.error(f"**Issue:** Your resume has no mention of {skill}.")
                st.markdown(f"""
**How to fix it:**
- Add {skill} to your skills section if you have any experience with it
- Build a small project using {skill} and add it to your portfolio
- Take a short course or certification to gain foundational knowledge
- Even mentioning related tools can help bridge the gap
""")
            elif score <= 5:
                st.warning(
                    f"**Issue:** Your resume mentions {skill} briefly "
                    f"but doesn't demonstrate strong proficiency."
                )
                st.markdown(f"""
**How to fix it:**
- Add specific examples of how you used {skill} in projects
- Include metrics or outcomes from your {skill} experience
- List specific tools frameworks or versions you have worked with
""")
            else:
                st.info(
                    f"**Issue:** You have some {skill} experience "
                    f"but it could be more prominent."
                )
                st.markdown(f"""
**How to fix it:**
- Move {skill} higher in your skills section
- Add a dedicated bullet point highlighting your {skill} achievements
- Quantify your {skill} experience with specific numbers or results
""")


# ── Feedback formatter ────────────────────────────────────────────────────────

def _format_feedback(text: str) -> str:
    import re

    lines = text.split('\n')
    fixed = []
    for line in lines:
        line = line.strip()
        if not line:
            fixed.append('')
            continue
        if line.startswith('###'):
            section_kw = ['strength', 'weakness', 'recommend', 'ats',
                          'format', 'skill', 'gap', 'interview', 'closing']
            if any(kw in line.lower() for kw in section_kw):
                fixed.append(line)
            else:
                clean = re.sub(r'^#+\s*', '', line)
                fixed.append(f'- **{clean}**')
        else:
            fixed.append(line)

    text = '\n'.join(fixed)
    text = re.sub(r'\s*•\s*',        '\n\n- ',        text)
    text = re.sub(r'\[(Critical|Moderate|Minor)\]', r'**[\1]**', text)
    text = re.sub(r'\*\*Before:\*\*', '\n\n**Before:**', text)
    text = re.sub(r'\*\*After:\*\*',  '\n**After:**',    text)
    text = re.sub(r'\*\*Why:\*\*',    '\n**Why:**',      text)
    text = re.sub(r'\n{3,}',          '\n\n',            text)
    return text.strip()


# ── CrewAI results renderer ───────────────────────────────────────────────────

def _render_crew_results(crew: dict, resume, tv: dict) -> None:
    st.success("🎉 CrewAI analysis complete!")
    with st.expander("📋 JD Analysis (Agent 1)", expanded=True):
        st.markdown(crew["jd_analysis"])
    with st.expander("🔍 Resume Critique (Agent 2)", expanded=True):
        st.markdown(crew["critique"])
    with st.expander("📈 Market Intelligence (Agent 3)", expanded=False):
        st.markdown(crew["market"])
    with st.expander("✍ Resume Rewrites (Agent 4)", expanded=True):
        st.markdown(crew["rewrite"])
    with st.expander("🎤 Interview Prep (Agent 5)", expanded=True):
        st.markdown(crew["interview"])
    st.divider()
    st.download_button(
        "📥 Download Full CrewAI Report",
        crew["full_report"],
        f"crew_analysis_{datetime.now():%Y%m%d_%H%M%S}.txt",
        "text/plain", use_container_width=True,
    )
    st.balloons()


# ── Scan animation ────────────────────────────────────────────────────────────

def _scan_animation(tv: dict) -> None:
    st.markdown(f"""
<div style="position:relative;width:150px;height:170px;margin:0 auto;
     display:flex;align-items:center;justify-content:center;">
  <div style="position:absolute;width:170px;height:170px;border-radius:50%;
       border:1.5px dashed {tv['border']};animation:orbitSpin 9s linear infinite;"></div>
  <div style="position:relative;width:110px;height:150px;background:{tv['card']};
       border:1.5px solid {tv['border']};border-radius:10px;overflow:hidden;
       animation:docFloat 3.2s ease-in-out infinite;">
    <div style="position:absolute;left:0;top:0;width:100%;height:22px;
         background:linear-gradient(180deg,rgba(99,102,241,0),
         rgba(99,102,241,.45),rgba(99,102,241,0));
         animation:scanMove 2.4s ease-in-out infinite;"></div>
    <div style="height:7px;margin:12px 12px 0;border-radius:4px;
         background:#818CF8;opacity:.55;"></div>
    <div style="height:7px;margin:10px 12px 0;width:70%;border-radius:4px;
         background:#818CF8;opacity:.55;"></div>
    <div style="height:7px;margin:10px 12px 0;width:85%;border-radius:4px;
         background:#818CF8;opacity:.55;"></div>
    <div style="height:7px;margin:10px 12px 0;width:55%;border-radius:4px;
         background:#818CF8;opacity:.55;"></div>
  </div>
</div>
<style>
@keyframes orbitSpin{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}
@keyframes docFloat{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-6px)}}}}
@keyframes scanMove{{0%{{top:-10%}}50%{{top:95%}}100%{{top:-10%}}}}
</style>""", unsafe_allow_html=True)