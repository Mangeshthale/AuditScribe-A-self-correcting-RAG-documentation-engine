# AuditScribe - Self-Correcting RAG Documentation Engine

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-red)](https://auditscribe-a-self-correcting-rag-documentation-engine.streamlit.app/)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

A production-grade agentic RAG pipeline that **retrieves, verifies, and documents** answers from your knowledge base - with automatic hallucination detection and web search fallback when vector DB confidence is insufficient.

🔗 **[Live Demo](https://auditscribe-a-self-correcting-rag-documentation-engine.streamlit.app/)**

---

## What Problem Does It Solve?

Standard RAG systems retrieve blindly - they return whatever the vector DB finds, even when the context is weak or irrelevant. AuditScribe adds a **self-correction loop**: if retrieved context isn't good enough, the system falls back to live web search. A Critic agent then checks for hallucinations before a Writer agent produces the final documentation.

---

## Architecture

```
User Query
    │
    ▼
LangGraph State Machine
    │
    ├──► ChromaDB Vector Retrieval (BGE-M3 embeddings)
    │         │
    │    [Sufficient context?]
    │         │
    │    NO ──► Tavily Web Search Fallback
    │         │
    ▼         ▼
     CrewAI Multi-Agent System
         │
         ├──► Critic Agent (hallucination detection)
         │
         └──► Writer Agent (structured Markdown output)
                   │
                   ▼
           Ragas Evaluation Score
           (Faithfulness + Answer Relevancy)
```

---

## Key Features

- **Self-correcting retrieval** via LangGraph state machines - automatically detects low-confidence retrieval and triggers web search
- **Multi-agent verification** using CrewAI - Critic agent flags hallucinations, Writer agent generates clean Markdown documentation
- **Real-time quality scoring** via Ragas - every query is evaluated for Faithfulness and Answer Relevancy at inference time
- **BAAI/bge-en-large-v1.5 embeddings** with ChromaDB for high-quality semantic retrieval
- **Powered by Groq (Llama 3.1 8B)** for fast inference
- **Document ingestion pipeline** via ingest.py - load and embed your own documents into ChromaDB with one command

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| Multi-Agent | CrewAI |
| LLM | Groq (Llama 3.1 8B) |
| Embeddings | BGE-M3 |
| Vector DB | ChromaDB |
| Evaluation | Ragas |
| Web Fallback | Tavily Search |
| UI | Streamlit |

---

## Run Locally

```bash
git clone https://github.com/Mangeshthale/AuditScribe-A-self-correcting-RAG-documentation-engine
cd AuditScribe-A-self-correcting-RAG-documentation-engine
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
```

```bash
streamlit run src/app.py
```

---

## Project Structure

```
AuditScribe/
├── src/
│   ├── agents/
│   │   ├── graph.py        # LangGraph pipeline & state machine
│   │   └── tools.py        # Tavily search + retrieval tools
│   ├── crew/
│   │   ├── agents.py       # CrewAI Critic + Writer agent definitions
│   │   └── tasks.py        # Task definitions for each agent
│   ├── eval/
│   │   └── evaluator.py    # Ragas scoring (Faithfulness + Relevancy)
│   ├── utils/
│   │   └── rate_limit.py   # API rate limiting utility
│   ├── app.py              # Streamlit UI entry point
│   ├── ingest.py           # Document ingestion → ChromaDB
│   └── main.py             # Main pipeline orchestration
├── data/                   # Sample documents
├── requirements.txt
└── README.md
```

---

## Author

**Mangesh Thale** - [LinkedIn](https://www.linkedin.com/in/mangesh-thale/) | [GitHub](https://github.com/Mangeshthale)
