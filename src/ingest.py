# src/ingest.py
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from agents.tools import get_embeddings  # reuse cached singleton — never create a second instance
CHROMA_DIR = "./data/chroma_db"
COLLECTION = "tech-docs"

splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)


def ingest_pdf(file_path: str) -> int:
    """Load a PDF, chunk it, embed into Chroma. Returns chunk count."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    chunks = splitter.split_documents(docs)
    _add_to_store(chunks)
    return len(chunks)


def ingest_url(url: str) -> int:
    """Scrape a webpage, chunk it, embed into Chroma. Returns chunk count."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    chunks = splitter.split_documents(docs)
    _add_to_store(chunks)
    return len(chunks)


def _add_to_store(chunks):
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=get_embeddings(),
        collection_name=COLLECTION,
    )
    vectorstore.add_documents(chunks)