# src/agents/graph.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from utils.rate_limit import groq_retry_decorator
from agents.tools import get_retriever, get_web_search_tool

# ── DO NOT instantiate get_web_search_tool() here at module level ──
# It reads TAVILY_API_KEY at call time, so keep it inside retrieve()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

GENERATE_PROMPT = ChatPromptTemplate.from_template(
    "You are a senior software engineer and technical assistant.\n\n"
    "## Instructions\n"
    "- Answer the question using ONLY the information provided in the context below.\n"
    "- Do NOT use any prior knowledge, assumptions, or information outside the given context.\n"
    "- If the context does not contain enough information to answer the question confidently, "
    "respond with exactly: 'NOT_FOUND_IN_DOCS' — do not guess or fabricate an answer.\n"
    "- If 'NOT_FOUND_IN_DOCS' is returned, a web search (Tavily) will be triggered automatically as a fallback.\n"
    "- Be concise, precise, and technical. Avoid filler phrases like 'Based on the context...'.\n"
    "- If the answer is partial (some info found, some missing), share what you found "
    "and clearly flag the gaps.\n\n"
    "## Context (from attached documents)\n"
    "{context}\n\n"
    "## Question\n"
    "{question}\n\n"
    "## Answer"
)

class AgentState(TypedDict):
    question: str
    generation: str
    documents: List[str]
    iterations: int

def retrieve(state):
    print("---RETRIEVING---")
    retriever = get_retriever()
    docs = retriever.invoke(state["question"])
    chunks = [d.page_content for d in docs]

    # If vector DB returns nothing useful, fall back to Tavily web search
    if not chunks or all(len(c.strip()) < 50 for c in chunks):
        print("---VECTOR DB EMPTY, FALLING BACK TO WEB SEARCH---")
        # Instantiated here — TAVILY_API_KEY is guaranteed to be in env by now
        web_results = get_web_search_tool().invoke(state["question"])
        if isinstance(web_results, list):
            chunks = [r.get("content", "") for r in web_results]
        else:
            chunks = [str(web_results)]

    return {"documents": chunks, "iterations": state["iterations"] + 1}

def grade_documents(state):
    if state["documents"] and state["iterations"] < 2:
        return "generate"
    return "generate"

@groq_retry_decorator
def call_llm(state):
    context = "\n\n".join(state["documents"]) if state["documents"] else "No context found."
    chain = GENERATE_PROMPT | llm
    response = chain.invoke({"context": context, "question": state["question"]})
    return response.content

def generate(state):
    print("---GENERATING---")
    answer = call_llm(state)
    return {"generation": answer}

workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.set_entry_point("retrieve")
workflow.add_conditional_edges("retrieve", grade_documents, {
    "generate": "generate"
})
workflow.add_edge("generate", END)
app = workflow.compile()
