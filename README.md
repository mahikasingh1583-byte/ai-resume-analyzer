# 🚀 AI Resume Analyzer
https://ai-resume-analyzer-tpbljxbxpqblld9bh3eqgw.streamlit.app/

A multi-phase AI-powered resume analysis tool built with Streamlit, CrewAI, Firecrawl, and RAG.

---

## Project Structure

```
resume_analyzer/
├── app.py                  # Streamlit entry point
├── config.py               # Feature flags & API keys (all phases)
├── requirements.txt
├── .env.example
│
├── ui/                     # Streamlit UI components
│   ├── theme.py
│   ├── sidebar.py
│   ├── tab_analysis.py     # Main tab — integrates all phases
│   ├── tab_mentor.py
│   ├── tab_rewriter.py
│   └── tab_roadmap.py
│
├── utils/                  # Core utilities
│   ├── llm_client.py       # Unified Anthropic / OpenAI / Ollama client
│   ├── resume_parser.py    # PDF/DOCX parsing + ATS keyword scoring
│   └── prompts.py          # All LLM prompt builders in one place
│
├── tools/                  # External tool wrappers
│   └── firecrawl_tool.py   # Phase 2: Firecrawl job scraper
│
├── rag/                    # Phase 3: RAG pipeline
│   ├── rag_pipeline.py     # ChromaDB vector store + retrieval
│   └── build_corpus.py     # One-time corpus builder script
│
└── agents/                 # Phase 4: CrewAI multi-agent pipeline
    └── crew.py             # 5-agent crew definition
```

---

## Integration Roadmap

### ✅ Phase 1 — Clean Architecture + Claude API (Ship this first)

**Goal:** Replace Ollama with Claude/OpenAI API so the app works for anyone without a local GPU.

**Steps:**
```bash
# 1. Clone and install
pip install -r requirements.txt   # installs only Phase 1 deps at first

# 2. Configure
cp .env.example .env
# Edit .env: set LLM_BACKEND=anthropic, add ANTHROPIC_API_KEY

# 3. Run
streamlit run app.py
```

**What you gain:**
- Publicly deployable (Streamlit Community Cloud, Render)
- Clean modular architecture (interviewers can read the code)
- Separated concerns: llm_client / prompts / parser / ui
- All 4 tabs working: Analysis, Mentor, Rewriter, Roadmap

**Resume bullet:**
> Built a modular AI resume analyzer (Claude API, Streamlit) with ATS scoring, LLM-powered critique, and resume rewriting — deployed publicly on Streamlit Cloud

---

### 🔜 Phase 2 — Firecrawl (Live Job Scraping)

**Goal:** Let users paste a LinkedIn/Indeed URL instead of copying job text manually.

**Steps:**
```bash
# 1. Sign up at firecrawl.dev and get an API key

# 2. Install
pip install firecrawl-py

# 3. Enable in .env
USE_FIRECRAWL=true
FIRECRAWL_API_KEY=fc-your-key-here

# 4. Re-run — the JD input now shows a "Scrape URL" radio option
streamlit run app.py
```

**What you gain:**
- Users can paste any job URL — Firecrawl handles anti-bot, HTML stripping, markdown conversion
- You can also build your RAG corpus by scraping 200+ JDs (see Phase 3)

**Code touched:** `tools/firecrawl_tool.py` (already written), `ui/tab_analysis.py` (already integrated behind `USE_FIRECRAWL` flag)

**Resume addition:**
> Integrated Firecrawl web scraping to extract live job descriptions from LinkedIn/Indeed URLs — eliminated manual copy-paste for users

---

### 🔜 Phase 3 — RAG with ChromaDB (Market-Grounded Analysis)

**Goal:** Ground every analysis in real market data by retrieving similar job descriptions from a vector store.

**Steps:**
```bash
# 1. Install
pip install chromadb sentence-transformers

# 2. Build your corpus
# Option A: Add .txt files to rag/sample_jds/ (manual)
# Option B: Add URLs to rag/jd_urls.txt and run (requires Firecrawl):
python rag/build_corpus.py

# 3. Enable in .env
USE_RAG=true

# 4. Re-run
streamlit run app.py
```

**How it works:**
1. `build_corpus.py` scrapes/loads 100-300 job descriptions
2. `sentence-transformers` (`all-MiniLM-L6-v2`) embeds them into ChromaDB
3. At analysis time, the user's JD is embedded and the top-5 most similar JDs are retrieved
4. Those 5 JDs are injected into the LLM prompt as "market context"
5. The LLM now produces analysis grounded in what this role actually looks like across the market

**Code touched:** `rag/rag_pipeline.py`, `rag/build_corpus.py` (both already written)

**Resume addition:**
> Added RAG pipeline (ChromaDB + sentence-transformers) grounding analysis in a 300-JD market corpus — reduced vague/hallucinated feedback by anchoring LLM output in retrieved real-world role requirements

---

### 🔜 Phase 4 — CrewAI Multi-Agent Pipeline

**Goal:** Replace the single LLM call with 5 specialized agents that share context and produce a richer, more coherent report.

**Steps:**
```bash
# 1. Install
pip install crewai crewai-tools

# 2. Enable in .env
USE_CREW=true
CREW_VERBOSE=false   # set true to watch agents reason step-by-step

# 3. Re-run — analysis now uses the 5-agent pipeline
streamlit run app.py
```

**The 5 agents:**
| Agent | Role | Tools |
|-------|------|-------|
| JD Analyst | Extract structured requirements | RAG tool |
| Resume Critic | Evidence-based weakness finder | None |
| Market Researcher | Salary, culture, skill demand | Firecrawl search |
| Resume Rewriter | Before/After bullet rewrites | RAG tool |
| Interview Coach | Tailored Q&A + STAR frameworks | None |

**How agents share context:**
- `Process.sequential` — each task receives prior tasks' outputs
- `memory=True` — agents remember context across the whole crew run
- The Rewriter agent knows exactly what the Critic found wrong
- The Coach knows both the JD requirements AND the candidate's gaps

**Code touched:** `agents/crew.py` (already written)

**Resume addition:**
> Architected a 5-agent CrewAI pipeline with RAG-grounded JD analysis, market intelligence via Firecrawl, and LLM-driven resume rewriting — agents share sequential context producing coherent multi-perspective output

---

## Deployment (after Phase 1)

### Streamlit Community Cloud (free)
1. Push to GitHub
2. Go to share.streamlit.io → New app
3. Add secrets: `ANTHROPIC_API_KEY`, `LLM_BACKEND=anthropic`
4. Deploy

### Render / Railway
```bash
# Start command:
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

---

## The resume bullet (final form after all 4 phases)

> "Architected a 4-phase AI resume analyzer: Claude API-powered ATS scoring and critique (Phase 1), Firecrawl live job scraping from LinkedIn/Indeed (Phase 2), RAG pipeline with ChromaDB + sentence-transformers grounding analysis in a 300-JD market corpus (Phase 3), and a 5-agent CrewAI system with specialist agents for JD analysis, critique, market research, rewriting, and interview prep — deployed publicly on Streamlit Cloud"
