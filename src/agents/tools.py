# src/agents/tools.py
import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_tavily import TavilySearch
from functools import lru_cache


@lru_cache(maxsize=1)
def get_embeddings():
    """Cached BGE-M3 embeddings — loads once at startup, reused everywhere."""
    return HuggingFaceEmbeddings(model_name="BAAI/bge-m3")


def get_retriever():
    vectorstore = Chroma(
        persist_directory="./data/chroma_db",
        embedding_function=get_embeddings(),
        collection_name="tech-docs"
    )
    return vectorstore.as_retriever(search_kwargs={"k": 5})


# Used as fallback in graph.py when vector DB has no relevant results
def get_web_search_tool():
    return TavilySearch()
