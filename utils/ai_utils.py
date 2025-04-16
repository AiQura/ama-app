"""
OpenAI utils
"""

import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from openai import OpenAI

from langgraph_integration.ingestion import _get_retriever_id, get_retriever

def get_ai_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def retrieve_documents(query: str, files=None, links=None) -> list[str]:
    retriever = get_retriever(files if files is not None else [
    ], links if links is not None else [])

    documents = retriever.invoke(query)
    return [doc.page_content for doc in documents]

def simple_ai_retriever(query: str, files=None, links=None) -> list[str]:
    # Get collection name
    retriever_id = _get_retriever_id(files or [], links or [])
    collection_name = f"rag-chroma-{retriever_id}"

    embedding_function = SentenceTransformerEmbeddingFunction()
    chroma_client = chromadb.Client()
    chroma_collection = chroma_client.get_collection(collection_name, embedding_function=embedding_function)

    results = chroma_collection.query(query_texts=[query], n_results=5)
    return results['documents'][0]

