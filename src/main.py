# src/main.py
import os
import time
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    for key in ["GROQ_API_KEY", "TAVILY_API_KEY"]:
        if not os.getenv(key) and key in st.secrets:
            os.environ[key] = st.secrets[key]
except Exception:
    pass

from langchain_groq import ChatGroq
from agents.graph import app as reasoning_graph
from crew.agents import run_verification_crew
from eval.evaluator import run_evals

# Lighter model for suggestions — faster, cheaper
_suggestion_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)


def generate_suggestions(question: str, answer: str) -> list:
    """Generate 3 follow-up question suggestions based on Q&A."""
    try:
        prompt = (
            f"Based on this question and answer, suggest exactly 3 short follow-up "
            f"questions a user might ask next.\n"
            f"Return ONLY the 3 questions, one per line, no numbering, no explanation.\n\n"
            f"Question: {question}\n"
            f"Answer: {answer[:500]}"
        )
        response = _suggestion_llm.invoke(prompt)
        lines = [
            line.strip()
            for line in response.content.strip().split("\n")
            if line.strip() and not line.strip()[0].isdigit()
        ]
        return lines[:3]
    except Exception:
        return []


def run_sentinel(user_query: str, chat_history: list = []):
    print(f"\n🚀 Starting AuditScribe for: {user_query}")
    time.sleep(2)  # reduced from 3

    # Build readable history string for the LLM
    history_text = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    initial_state = {
        "question": user_query,
        "iterations": 0,
        "documents": [],
        "generation": "",
        "history": history_text.strip(),
        "source": "docs"
    }

    graph_output = reasoning_graph.invoke(initial_state)
    raw_answer = graph_output["generation"]
    source = graph_output.get("source", "docs")

    # Step 2: Multi-Agent Polish
    print("✨ Polishing with Multi-Agent Crew...")
    final_report = run_verification_crew(raw_answer)
    report_text = str(final_report.raw if hasattr(final_report, "raw") else final_report)

    # Step 3: Ragas Evaluation
    print("📊 Running Evaluation Gate...")
    scores = run_evals(
        [user_query],
        [report_text],
        [graph_output["documents"]]
    )

    # Step 4: Suggestions
    suggestions = generate_suggestions(user_query, report_text)

    return final_report, scores, suggestions, source


if __name__ == "__main__":
    query = "How do I implement a circuit breaker pattern in FastAPI?"
    report, quality_metrics, suggestions, source = run_sentinel(query)

    print("\n" + "=" * 30)
    print("FINAL AGENT REPORT")
    print("=" * 30)
    print(report)
    print("\nQUALITY SCORES:", quality_metrics)
    print("SOURCE:", source)
    print("SUGGESTED QUESTIONS:", suggestions)
