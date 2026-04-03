import os
from dotenv import load_dotenv
load_dotenv()
try:
    import streamlit as st
    for key in ["GROQ_API_KEY", "TAVILY_API_KEY"]:
        if not os.getenv(key) and key in st.secrets:
            os.environ[key] = st.secrets[key]
except Exception:
    pass
from agents.graph import app as reasoning_graph
from crew.agents import run_verification_crew
from eval.evaluator import run_evals



def run_sentinel(user_query: str):
    print(f"\n🚀 Starting Sentinel for: {user_query}")
    
    # Step 1: Reasoning Loop (LangGraph)
    # This finds the info and self-corrects if needed
    initial_state = {"question": user_query, "iterations": 0, "documents": [], "generation": ""}
    graph_output = reasoning_graph.invoke(initial_state)
    raw_answer = graph_output["generation"]
    
    # Step 2: Multi-Agent Polish (CrewAI)
    # Passes the raw answer to a Critic and an Editor
    print("✨ Polishing with Multi-Agent Crew...")
    final_report = run_verification_crew(raw_answer)
    
    # Step 3: Evaluation (Ragas)
    # Silently scores the output to ensure quality
    print("📊 Running Evaluation Gate...")
    scores = run_evals(
        [user_query], 
        [str(final_report)], 
        [graph_output["documents"]]
    )
    
    return final_report, scores

if __name__ == "__main__":
    query = "How do I implement a circuit breaker pattern in FastAPI?"
    report, quality_metrics = run_sentinel(query)
    
    print("\n" + "="*30)
    print("FINAL AGENT REPORT")
    print("="*30)
    print(report)
    print("\nQUALITY SCORES:", quality_metrics)
