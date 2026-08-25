# AuditScribe - Self-Correcting RAG Documentation Engine

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-red)](https://auditscribe-a-self-correcting-rag-documentation-engine.streamlit.app/)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

A production-grade agentic RAG pipeline that **retrieves, verifies, and documents** answers from your knowledge base - with automatic hallucination detection and web search fallback when vector DB confidence is insufficient.

🔗 **[Live Demo](https://auditscribe-a-self-correcting-rag-documentation-engine.streamlit.app/)**

---

## What Problem Does It Solve?

Standard RAG systems retrieve blindly - they return whatever the vector DB finds, even when the context is weak or irrelevant. AuditScribe adds a **self-correction loop**: if retrieved context isn't good enough, the system automatically falls back to live web search. A Critic agent then checks for hallucinations before a Writer agent produces the final documentation.

---

## Architecture

```
                        ┌─────────────────────┐
                        │   Streamlit Cloud    │
                        │      (UI Layer)      │
                        └──────────┬──────────┘
                                   │ HTTP (REST)
                                   ▼
                        ┌─────────────────────┐
                        │   FastAPI Backend    │  ← Render
                        │  /audit/run          │
                        │  /ingest/pdf         │
                        │  /ingest/url         │
                        └──────────┬──────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │     LangGraph State Machine    │
                   │                               │
                   │  ┌─────────────────────────┐  │
                   │  │ ChromaDB Vector Search   │  │
                   │  │ (BGE-large-en-v1.5)      │  │
                   │  └────────────┬────────────┘  │
                   │               │                │
                   │       [Sufficient context?]    │
                   │               │                │
                   │    NO ────────▼──────────┐     │
                   │               │          │     │
                   │               │   Tavily Web   │
                   │               │   Search       │
                   │               │          │     │
                   └───────────────┼──────────┘─────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │    CrewAI Multi-Agent System   │
                   │                               │
                   │  Critic Agent                 │
                   │  (hallucination detection)    │
                   │            +                  │
                   │  Writer Agent                 │
                   │  (structured Markdown output) │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │       Ragas Evaluation        │
                   │  Faithfulness + Relevancy     │
                   └───────────────────────────────┘
```

---

## Key Features

- **REST API backend** built with FastAPI - clean separation of UI and pipeline logic
- **Self-correcting retrieval** via LangGraph state machines - automatically detects low-confidence retrieval and triggers Tavily web search fallback
- **Multi-agent verification** using CrewAI - Critic agent validates facts silently, Writer agent generates clean Markdown documentation
- **Real-time quality scoring** via Ragas - every query scored for Faithfulness and Answer Relevancy at inference time
- **BAAI/bge-large-en-v1.5 embeddings** with ChromaDB for high-quality semantic retrieval
- **Powered by Groq** (gpt-oss-120b for generation, gpt-oss-20b for suggestions) for fast inference
- **Conversation memory** - the LLM retains context across the current session for follow-up questions
- **Suggested follow-up questions** - 3 contextual next questions generated after every answer
- **Document ingestion pipeline** - load PDFs or URLs directly from the UI into ChromaDB

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Backend | FastAPI + Uvicorn |
| Orchestration | LangGraph |
| Multi-Agent | CrewAI |
| LLM (Generation) | Groq - gpt-oss-120b |
| LLM (Suggestions) | Groq - gpt-oss-20b |
| Embeddings | BAAI/bge-large-en-v1.5 |
| Vector DB | ChromaDB |
| Evaluation | Ragas |
| Web Fallback | Tavily Search |
| UI | Streamlit |
| Backend Deploy | Render |
| UI Deploy | Streamlit Cloud |

---

## Run Locally

```bash
git clone https://github.com/Mangeshthale/AuditScribe-A-self-correcting-RAG-documentation-engine
cd AuditScribe-A-self-correcting-RAG-documentation-engine
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

Start the FastAPI backend (Terminal 1):
```bash
uvicorn src.api.main:app --reload --port 8000
```

Start the Streamlit UI (Terminal 2):
```bash
streamlit run src/app.py
```

Open `http://localhost:8501` in your browser.

---

## Deployment
Live at [auditscribe.streamlit.app](https://auditscribe-a-self-correcting-rag-documentation-engine.streamlit.app/) - 
FastAPI backend on Render, UI on Streamlit Cloud.
---

## Project Structure

```
AuditScribe/
├── src/
│   ├── agents/
│   │   ├── graph.py          # LangGraph pipeline & state machine
│   │   └── tools.py          # ChromaDB retriever + Tavily search
│   ├── api/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── schemas.py        # Pydantic request/response models
│   │   └── routes/
│   │       ├── audit.py      # POST /audit/run
│   │       └── ingest.py     # POST /ingest/pdf, /ingest/url
│   ├── crew/
│   │   ├── agents.py         # CrewAI Critic + Writer agent definitions
│   │   └── tasks.py          # Task descriptions for each agent
│   ├── eval/
│   │   └── evaluator.py      # Ragas scoring (Faithfulness + Relevancy)
│   ├── utils/
│   │   └── rate_limit.py     # Groq rate limit retry decorator
│   ├── app.py                # Streamlit UI
│   ├── ingest.py             # PDF + URL ingestion → ChromaDB
│   └── main.py               # Pipeline orchestration (run_sentinel)
├── data/                     # Sample documents
├── render.yaml               # Render deployment config
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/audit/run` | Run the full RAG + audit pipeline |
| `POST` | `/ingest/pdf` | Upload and index a PDF |
| `POST` | `/ingest/url` | Scrape and index a URL |

### Example Request

```bash
curl -X POST https://your-api.onrender.com/audit/run \
  -H "Content-Type: application/json" \
  -d '{"query": "How does a circuit breaker work in FastAPI?"}'
```

### Example Response

```json
{
  "report": "## Circuit Breaker Pattern in FastAPI\n...",
  "faithfulness": 0.87,
  "answer_relevancy": 0.91,
  "latency": 12.4,
  "source": "docs",
  "suggestions": [
    "What are the three states of a circuit breaker?",
    "How do I configure the timeout threshold?",
    "Which library is recommended for circuit breakers in Python?"
  ]
}
```

---

## Author

**Mangesh Thale** - [LinkedIn](https://www.linkedin.com/in/mangesh-thale/) | [GitHub](https://github.com/Mangeshthale)
