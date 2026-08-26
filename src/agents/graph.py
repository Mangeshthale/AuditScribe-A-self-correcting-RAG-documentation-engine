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

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# ── Clean prompt — no NOT_FOUND_IN_DOCS, no "technical" trigger word ─────────
GENERATE_PROMPT = ChatPromptTemplate.from_template(
    "You are a helpful assistant. Answer the user's question directly and clearly.\n\n"
    "## Previous Conversation\n"
    "{history}\n\n"
    "## Context\n"
    "{context}\n\n"
    "## Question\n"
    "{question}\n\n"
    "Answer using only the context above. Be direct and concise. "
    "If the context does not contain the answer, say in one sentence: "
    "'I could not find this in the provided content.'"
)


class AgentState(TypedDict):
    question: str
    generation: str
    documents: List[str]
    iterations: int
    history: str    # conversation history as formatted string
    source: str     # "docs" or "web"


def retrieve(state):
    print("---RETRIEVING---")
    retriever = get_retriever()
    docs = retriever.invoke(state["question"])
    chunks = [d.page_content for d in docs]

    # Only use doc chunks if they are actually meaningful
    useful = [c for c in chunks if len(c.strip()) > 50]

    if useful:
        print(f"---FOUND {len(useful)} USEFUL CHUNKS FROM DOCS---")
        return {
            "documents": useful,
            "source": "docs",
            "iterations": state["iterations"] + 1
        }

    # Nothing useful — fall back to Tavily web search
    print("---NO USEFUL CHUNKS FOUND, FALLING BACK TO TAVILY---")
    try:
        web_results = get_web_search_tool().invoke(state["question"])
        if isinstance(web_results, list):
            web_chunks = [r.get("content", "") for r in web_results]
        else:
            web_chunks = [str(web_results)]
    except Exception as e:
        print(f"---TAVILY FAILED: {e}---")
        web_chunks = ["No content could be retrieved."]

    return {
        "documents": web_chunks,
        "source": "web",
        "iterations": state["iterations"] + 1
    }


def grade_documents(state):
    return "generate"


@groq_retry_decorator
def call_llm(state):
    context = "\n\n".join(state["documents"]) if state["documents"] else "No context available."
    history = state.get("history", "") or "No previous conversation."
    chain = GENERATE_PROMPT | llm
    response = chain.invoke({
        "context": context,
        "question": state["question"],
        "history": history,
    })
    return response.content


def generate(state):
    print("---GENERATING---")
    answer = call_llm(state)
    return {
        "generation": answer,
        "documents": state["documents"],
        "source": state.get("source", "docs")
    }


workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_conditional_edges("retrieve", grade_documents, {
    "generate": "generate"
})
workflow.add_edge("generate", END)

app = workflow.compile()
