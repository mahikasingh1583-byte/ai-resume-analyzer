# 🚀 AI Resume Analyzer

> AI-powered resume toolkit with ATS scoring, live job scraping, RAG-grounded analysis, and LLM critique — built with Groq LLaMA 3, Firecrawl, ChromaDB, and Streamlit.

<!-- Add your demo GIF here after editing your video:
![Demo](demo.gif)


-->

##(https://ai-resume-analyzer-tpbljxbxpqblld9bh3eqgw.streamlit.app/)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 ATS Scoring | AI matches resume against job description and gives a real 0-100 score |
| 🌐 Live Job Scraping | Paste any LinkedIn or Indeed URL — Firecrawl fetches the JD automatically |
| 🧠 RAG-Grounded Analysis | Retrieves 5 similar real-world JDs from ChromaDB to ground every insight in market data |
| 🚨 Skill Gap Detection | Missing skills scored 0–10 with expandable fix recommendations |
| 🤖 AI Resume Critique | Line-by-line weaknesses with Before → After rewrites and severity tags |
| ✍️ Resume Rewriter | Rewrites weak bullets with strong action verbs in 3 tones |
| 🎓 Career Mentor Chat | Personalized AI career advisor using your resume as context |
| 📚 Learning Roadmap | Week-by-week plan to close skill gaps with specific resources |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| LLM | Groq LLaMA 3.1 8b (free, fast inference) |
| Job Scraping | Firecrawl (anti-bot handling, HTML stripping) |
| Vector Store | ChromaDB (local persistent store) |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| PDF/DOCX Parsing | pypdf + python-docx |
| Deployment | Streamlit Community Cloud |

---

## 🏗 Architecture — 3 Phase Build

### ✅ Phase 1 — Groq API + Clean Modular Architecture
Replaced local Ollama with Groq's free cloud API so the app works for anyone. Split one 600-line file into proper modules with separated concerns.

```
utils/llm_client.py    → unified LLM interface (Groq/OpenAI/Anthropic)
utils/resume_parser.py → PDF/DOCX parsing + AI-powered ATS scoring
utils/prompts.py       → all LLM prompts in one place
ui/                    → separated tab components
config.py              → all feature flags in one place
```

### ✅ Phase 2 — Firecrawl Live Job Scraping
Users paste a LinkedIn or Indeed URL instead of manually copying job descriptions. Firecrawl handles anti-bot protection, strips navigation/ads, and returns clean markdown text.

### ✅ Phase 3 — RAG Pipeline with ChromaDB
Embeds 29 real job descriptions into ChromaDB using sentence-transformers. At analysis time retrieves the 5 most similar JDs and injects them into the LLM prompt — grounding analysis in real market data instead of one example JD.

```
rag/sample_jds/     → 29 real job descriptions across 15+ roles
rag/build_corpus.py → one-time embedding script
rag/rag_pipeline.py → retrieval + context formatting
```

---

## 📁 Project Structure

```
resume_analyzer/
├── app.py                   # Streamlit entry point
├── config.py                # Feature flags (USE_FIRECRAWL, USE_RAG)
│
├── ui/
│   ├── theme.py             # Dark/light mode + 6 color themes
│   ├── sidebar.py           # Settings + analysis history
│   ├── tab_analysis.py      # Main analysis tab
│   ├── tab_mentor.py        # Career mentor chatbot
│   ├── tab_rewriter.py      # Resume rewriter
│   └── tab_roadmap.py       # Learning roadmap generator
│
├── utils/
│   ├── llm_client.py        # Unified LLM client
│   ├── resume_parser.py     # PDF/DOCX parsing + AI skill extraction
│   └── prompts.py           # All LLM prompt builders
│
├── tools/
│   └── firecrawl_tool.py    # Firecrawl job scraper
│
└── rag/
    ├── rag_pipeline.py      # ChromaDB vector store + retrieval
    ├── build_corpus.py      # Corpus builder (run once)
    └── sample_jds/          # 29 real job descriptions
```

---

## 🚀 Run Locally

```bash
# 1. Clone
git clone https://github.com/mahikasingh1583-byte/ai-resume-analyzer
cd ai-resume-analyzer

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Fill in your keys (see below)

# 4. Build RAG corpus (first time only)
python rag/build_corpus.py

# 5. Run
streamlit run app.py
```

### Environment Variables

```bash
LLM_BACKEND=openai
OPENAI_API_KEY=gsk_your_groq_key    # Get free at console.groq.com
USE_FIRECRAWL=true
FIRECRAWL_API_KEY=fc_your_key       # Get free at firecrawl.dev
USE_RAG=true
```

---

## 👩‍💻 Built by

**Mahika Singh** 
[GitHub](https://github.com/mahikasingh1583-byte)
