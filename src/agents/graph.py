# src/agents/graph.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from utils.rate_limit import groq_retry_decorator
from agents.tools import get_retriever, get_web_search_tool()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

GENERATE_PROMPT = ChatPromptTemplate.from_template(
    "You are a senior software engineer. Answer the question using ONLY the context below.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n\n"
    "Give a concise, accurate technical answer."
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
        web_results = web_search_tool.invoke(state["question"])
        # Tavily returns a string or list depending on version
        if isinstance(web_results, list):
            chunks = [r.get("content", "") for r in web_results]
        else:
            chunks = [str(web_results)]

    return {"documents": chunks, "iterations": state["iterations"] + 1}


def grade_documents(state):
    # Simple relevance gate: if we have docs, generate; else retry once
    if state["documents"] and state["iterations"] < 2:
        return "generate"
    return "generate"  # always generate; extend with real grading if needed


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
