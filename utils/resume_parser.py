"""
utils/resume_parser.py — extract plain text from PDF/DOCX files
and analyze resume against job description using AI-powered skill extraction.
"""

from __future__ import annotations
import re
import streamlit as st


# ── Text extraction ───────────────────────────────────────────────────────────

def extract_text(uploaded_file) -> str:
    """
    Extract plain text from an uploaded PDF or DOCX file.
    Returns '' on failure and shows a friendly Streamlit error.
    """
    filename = uploaded_file.name.lower()
    try:
        if filename.endswith(".docx"):
            from docx import Document
            doc = Document(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs)

        # Default → PDF
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages)

    except Exception as exc:
        st.error(f"⚠ Couldn't read '{uploaded_file.name}': {exc}")
        return ""


# ── Skills database (used as fallback only) ───────────────────────────────────

SKILLS_DB: list[str] = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "SQL", "R",
    "React", "Angular", "Vue", "Node.js", "Django", "Flask", "FastAPI",
    "Spring Boot", "HTML", "CSS", "Tailwind", "Bootstrap",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Jenkins",
    "Git", "GitHub", "Linux", "Terraform", "Ansible",
    "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch",
    "Scikit-learn", "Pandas", "NumPy", "Data Analysis", "Data Visualization",
    "Power BI", "Tableau", "Excel",
    "MongoDB", "PostgreSQL", "MySQL", "Redis", "Firebase",
    "REST API", "GraphQL", "Microservices", "Agile", "Scrum",
    "Project Management", "Communication", "Leadership", "Problem Solving",
    "Team Collaboration", "Testing", "Unit Testing", "DevOps",
    "Cloud Computing", "Cybersecurity", "Blockchain",
    "LangChain", "CrewAI", "RAG", "Vector Database", "ChromaDB", "Pinecone",
    "sentence-transformers", "Embeddings", "Firecrawl", "OpenAI API",
    "Anthropic API", "Streamlit", "Hugging Face",
]

STOPWORDS: set[str] = set("""
the a an and or for with to of in on at is are be will this that as your
you we our experience years strong working knowledge ability skills role
team work using etc into across over per via not also more most than other
""".split())


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


_SKILLS_NORM: dict[str, str] = {_normalize(s): s for s in SKILLS_DB}


# ── Main analyze function ─────────────────────────────────────────────────────

def analyze_resume(resume_text: str, jd_text: str) -> dict:
    """
    AI-powered skill extraction and ATS scoring.
    Falls back to keyword matching if AI call fails.
    """
    from utils.llm_client import ask_llm

    prompt = f"""You are a strict ATS recruiter. Your job is to find REAL skill gaps.

STEP 1 - Read this job description carefully and identify every required skill, tool, technology, certification, and domain knowledge:
JOB DESCRIPTION:
{jd_text[:1500]}

STEP 2 - Read this resume carefully:
RESUME:
{resume_text[:2000]}

STEP 3 - Compare them strictly:
- MATCHED_SKILLS = skills that appear in BOTH the job description AND the resume
- MISSING_SKILLS = skills the job description REQUIRES or PREFERS that are NOT in the resume

Examples of what counts as missing:
- JD says "AWS" but resume has no AWS → AWS is MISSING
- JD says "Docker" but resume has no Docker → Docker is MISSING
- JD says "React.js" but resume only has "JavaScript" → React.js is MISSING
- JD says "5 years experience" but resume shows 1 year → flag as experience gap
- JD mentions a certification (e.g. CISSP, AWS Certified) not on resume → MISSING

Respond ONLY in this exact format with no extra text:
MATCHED_SKILLS: skill1, skill2, skill3
MISSING_SKILLS: skill1, skill2, skill3, skill4, skill5
ATS_SCORE: 45

You MUST list at least 5 missing skills. There are always gaps — look harder."""

    try:
        response = ask_llm(prompt, max_tokens=400)

        matched = []
        missing = []
        score   = 50

        # Robust regex — works whether AI uses newlines or not
        matched_match = re.search(
            r"MATCHED_SKILLS:\s*(.+?)(?=MISSING_SKILLS:|ATS_SCORE:|$)",
            response, re.DOTALL | re.IGNORECASE
        )
        missing_match = re.search(
            r"MISSING_SKILLS:\s*(.+?)(?=ATS_SCORE:|MATCHED_SKILLS:|$)",
            response, re.DOTALL | re.IGNORECASE
        )
        score_match = re.search(
            r"ATS_SCORE:\s*(\d+)",
            response, re.IGNORECASE
        )

        if matched_match:
            raw = matched_match.group(1).strip()
            matched = [
                s.strip() for s in raw.split(",")
                if s.strip() and s.strip().lower() not in ("none", "n/a", "")
            ]

        if missing_match:
            raw = missing_match.group(1).strip()
            missing = [
                s.strip() for s in raw.split(",")
                if s.strip() and s.strip().lower() not in ("none", "n/a", "")
            ]

        if score_match:
            score = int(score_match.group(1))
            score = max(8, min(97, score))

        # If missing is still empty — fire a simpler fallback prompt
        if not missing:
            simple = ask_llm(
                f"""List exactly 6 specific skills, tools, or technologies that 
this job requires but this resume does NOT mention.

Job: {jd_text[:800]}
Resume: {resume_text[:800]}

Reply with ONLY a comma separated list. No explanations. No numbering.""",
                max_tokens=150
            )
            missing = [
                s.strip() for s in simple.split(",")
                if s.strip() and len(s.strip()) > 1
            ][:10]

        # Last resort — keyword fallback
        if not matched and not missing:
            return _keyword_analyze(resume_text, jd_text)

        return {
            "score":   score,
            "matched": matched[:12],
            "missing": missing[:10],
        }

    except Exception:
        return _keyword_analyze(resume_text, jd_text)


# ── Keyword fallback ──────────────────────────────────────────────────────────

def _keyword_analyze(resume_text: str, jd_text: str) -> dict:
    """
    Fallback keyword-based ATS scoring.
    Used only when AI call fails completely.
    """
    resume_norm = _normalize(resume_text)
    jd_norm     = _normalize(jd_text)

    jd_skills = [orig for norm, orig in _SKILLS_NORM.items() if norm in jd_norm]
    if not jd_skills:
        jd_skills = [
            orig for norm, orig in _SKILLS_NORM.items()
            if norm in resume_norm
        ][:10]

    matched = [s for s in jd_skills if _normalize(s) in resume_norm]
    missing = [s for s in jd_skills if s not in matched]

    skill_score  = (len(matched) / len(jd_skills) * 100) if jd_skills else 50
    jd_words     = set(re.findall(r"[a-zA-Z]{3,}", jd_text.lower())) - STOPWORDS
    resume_words = set(re.findall(r"[a-zA-Z]{3,}", resume_text.lower())) - STOPWORDS
    word_score   = min(100, len(jd_words & resume_words) / max(len(jd_words), 1) * 100)

    final = round(skill_score * 0.7 + word_score * 0.3)
    final = max(8, min(97, final))

    return {
        "score":   final,
        "matched": matched[:12],
        "missing": missing[:10],
    }