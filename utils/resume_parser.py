"""
utils/resume_parser.py — extract plain text from PDF and DOCX files.
"""

from __future__ import annotations
import re
import streamlit as st


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


# ── ATS keyword matching ──────────────────────────────────────────────────────

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
    # Phase 3/4 additions — AI/ML stack
    "LangChain", "CrewAI", "RAG", "Vector Database", "ChromaDB", "Pinecone",
    "sentence-transformers", "Embeddings", "Firecrawl", "OpenAI API",
    "Anthropic API", "Streamlit", "FastAPI", "Hugging Face",
]

STOPWORDS: set[str] = set("""
the a an and or for with to of in on at is are be will this that as your
you we our experience years strong working knowledge ability skills role
team work using etc into across over per via not also more most than other
""".split())


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


_SKILLS_NORM: dict[str, str] = {_normalize(s): s for s in SKILLS_DB}


def analyze_resume(resume_text: str, jd_text: str) -> dict:
    """
    Keyword-based ATS scoring. Returns:
        {"score": int, "matched": list[str], "missing": list[str]}

    Phase 3 upgrade: when USE_RAG=True, the caller passes retrieved JD
    context as additional text — this function stays the same, the calling
    code enriches jd_text before passing it.
    """
    resume_norm = _normalize(resume_text)
    jd_norm     = _normalize(jd_text)

    jd_skills = [orig for norm, orig in _SKILLS_NORM.items() if norm in jd_norm]
    if not jd_skills:
        jd_skills = [orig for norm, orig in _SKILLS_NORM.items() if norm in resume_norm][:10]

    matched = [s for s in jd_skills if _normalize(s) in resume_norm]
    missing = [s for s in jd_skills if s not in matched]

    skill_score = (len(matched) / len(jd_skills) * 100) if jd_skills else 50

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
