"""
agents/crew.py — Phase 4: CrewAI multi-agent resume analysis pipeline.

Agents:
    1. JD Analyst       — extracts structured requirements (uses RAG tool)
    2. Resume Critic    — evidence-based weakness identification
    3. Market Researcher— live salary/culture data (uses Firecrawl search)
    4. Resume Rewriter  — rewrites bullets using critic output + RAG examples
    5. Interview Coach  — tailored Q&A + STAR frameworks

To activate:
    1. pip install crewai crewai-tools
    2. Set USE_CREW=true in .env
    3. Ensure LLM_BACKEND and API key are set
"""

from __future__ import annotations
from config import USE_CREW, CREW_VERBOSE, LLM_BACKEND, ANTHROPIC_API_KEY, OPENAI_API_KEY
from utils.prompts import (
    JD_ANALYST_BACKSTORY, RESUME_CRITIC_BACKSTORY,
    MARKET_RESEARCHER_BACKSTORY, REWRITER_BACKSTORY, INTERVIEW_COACH_BACKSTORY,
)


def is_available() -> bool:
    if not USE_CREW:
        return False
    try:
        import crewai  # noqa: F401
        return True
    except ImportError:
        return False


def _make_llm():
    """Create the LLM instance for CrewAI agents."""
    from crewai import LLM

    if LLM_BACKEND == "anthropic":
        return LLM(model="anthropic/claude-sonnet-4-6", api_key=ANTHROPIC_API_KEY)
    elif LLM_BACKEND == "openai":
        return LLM(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
    else:
        # Ollama via LiteLLM (CrewAI uses LiteLLM under the hood)
        return LLM(model="ollama/qwen3:4b", base_url="http://localhost:11434")


def _make_rag_tool():
    """Wrap the RAG pipeline as a CrewAI-compatible tool."""
    from crewai_tools import BaseTool
    from rag.rag_pipeline import retrieve_similar_jds, format_rag_context

    class JobMarketRAGTool(BaseTool):
        name: str = "Job Market Knowledge Base"
        description: str = (
            "Retrieves similar real-world job descriptions from the market corpus. "
            "Input: a job title or key skills query. "
            "Output: context from 3-5 similar job postings."
        )

        def _run(self, query: str) -> str:
            similar = retrieve_similar_jds(query, k=3)
            return format_rag_context(similar) or "No similar jobs found in corpus."

    return JobMarketRAGTool()


def _make_firecrawl_tool():
    """Wrap Firecrawl search as a CrewAI tool for market research."""
    try:
        from crewai_tools import FirecrawlSearchTool
        return FirecrawlSearchTool()
    except Exception:
        # Fallback: simple web search stub (replace with SerperDevTool etc.)
        from crewai_tools import BaseTool

        class WebResearchTool(BaseTool):
            name: str = "Web Research"
            description: str = "Search for salary data and market trends. Input: search query."

            def _run(self, query: str) -> str:
                return f"[Web research for '{query}' — configure Firecrawl or Serper for live results]"

        return WebResearchTool()


def run_crew_analysis(resume_text: str, jd_text: str) -> dict[str, str]:
    """
    Run the full CrewAI multi-agent pipeline.

    Returns:
        {
          "jd_analysis": str,
          "critique":    str,
          "market":      str,
          "rewrite":     str,
          "interview":   str,
          "full_report": str,
        }
    """
    if not is_available():
        raise RuntimeError("CrewAI not enabled. Set USE_CREW=true and pip install crewai crewai-tools.")

    from crewai import Agent, Task, Crew, Process

    llm          = _make_llm()
    rag_tool     = _make_rag_tool()
    market_tool  = _make_firecrawl_tool()

    # ── Agents ────────────────────────────────────────────────────────────────
    jd_analyst = Agent(
        role="Job Description Analyst",
        goal="Extract a structured, prioritised list of requirements from the job description",
        backstory=JD_ANALYST_BACKSTORY,
        tools=[rag_tool],
        llm=llm,
        verbose=CREW_VERBOSE,
    )

    critic = Agent(
        role="Senior Resume Critic",
        goal="Identify specific, evidence-based weaknesses in the resume vs the JD requirements",
        backstory=RESUME_CRITIC_BACKSTORY,
        llm=llm,
        verbose=CREW_VERBOSE,
    )

    researcher = Agent(
        role="Market Intelligence Researcher",
        goal="Find current salary ranges, company culture signals, and skill demand trends",
        backstory=MARKET_RESEARCHER_BACKSTORY,
        tools=[market_tool],
        llm=llm,
        verbose=CREW_VERBOSE,
    )

    rewriter = Agent(
        role="Professional Resume Writer",
        goal="Rewrite weak resume bullets using the critic's feedback without inventing facts",
        backstory=REWRITER_BACKSTORY,
        tools=[rag_tool],
        llm=llm,
        verbose=CREW_VERBOSE,
    )

    coach = Agent(
        role="Interview Coach",
        goal="Generate tailored interview questions with STAR-method answer frameworks",
        backstory=INTERVIEW_COACH_BACKSTORY,
        llm=llm,
        verbose=CREW_VERBOSE,
    )

    # ── Tasks (sequential — each gets the prior agent's output) ───────────────
    task_jd = Task(
        description=(
            f"Analyse this job description and produce a structured breakdown:\n\n{jd_text[:1200]}\n\n"
            "Output: must-have skills, nice-to-have skills, seniority level, red-flag requirements."
        ),
        expected_output="Structured markdown list of requirements with priority tags.",
        agent=jd_analyst,
    )

    task_critique = Task(
        description=(
            f"Using the JD analysis above, critique this resume:\n\n{resume_text[:2500]}\n\n"
            "Reference specific lines. Tag severity [Critical/Moderate/Minor]."
        ),
        expected_output="5-7 specific, evidence-based weaknesses with severity tags.",
        agent=critic,
        context=[task_jd],
    )

    task_market = Task(
        description=(
            "Research current market data for this role: "
            "salary range (location-agnostic), top companies hiring, "
            "most in-demand skills, and one culture/review insight."
        ),
        expected_output="Concise market intelligence report in markdown.",
        agent=researcher,
        context=[task_jd],
    )

    task_rewrite = Task(
        description=(
            "Rewrite the 5 weakest resume bullets identified by the critic. "
            "Use the same facts — never invent experience or metrics. "
            "Format as Before / After pairs with one-line rationale."
        ),
        expected_output="5 Before/After bullet rewrites with rationale.",
        agent=rewriter,
        context=[task_critique],
    )

    task_interview = Task(
        description=(
            "Generate 5 tailored interview questions for this candidate applying to this role. "
            "For each question, provide a STAR-method answer framework using the candidate's actual experience."
        ),
        expected_output="5 Q&A pairs with STAR frameworks referencing actual resume content.",
        agent=coach,
        context=[task_jd, task_critique],
    )

    # ── Crew ─────────────────────────────────────────────────────────────────
    crew = Crew(
        agents=[jd_analyst, critic, researcher, rewriter, coach],
        tasks=[task_jd, task_critique, task_market, task_rewrite, task_interview],
        process=Process.sequential,
        memory=True,
        verbose=CREW_VERBOSE,
    )

    crew.kickoff(inputs={"resume": resume_text, "jd": jd_text})

    # Collect individual outputs
    outputs = [t.output.raw if hasattr(t.output, "raw") else str(t.output)
               for t in [task_jd, task_critique, task_market, task_rewrite, task_interview]]

    full = "\n\n---\n\n".join([
        f"## JD Analysis\n{outputs[0]}",
        f"## Resume Critique\n{outputs[1]}",
        f"## Market Intelligence\n{outputs[2]}",
        f"## Resume Rewrites\n{outputs[3]}",
        f"## Interview Prep\n{outputs[4]}",
    ])

    return {
        "jd_analysis": outputs[0],
        "critique":    outputs[1],
        "market":      outputs[2],
        "rewrite":     outputs[3],
        "interview":   outputs[4],
        "full_report": full,
    }
