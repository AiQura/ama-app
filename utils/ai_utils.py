"""
OpenAI utils
"""

import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import numpy as np
from openai import OpenAI
from sentence_transformers import CrossEncoder
import streamlit as st

from modules.file.file_model import FileModel
from modules.link.link_model import LinkModel

# Check for environment variables
def check_api_key():
    """Check if OpenAI API key is available"""
    return "OPENAI_API_KEY" in os.environ

@st.cache_resource
def get_ai_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@st.cache_resource
def get_chroma_client():
    return chromadb.Client()

def get_retriever_id(files: list[FileModel], links: list[LinkModel]) -> str:
    """Generate a unique ID for a set of files and links"""
    # Sort and combine file IDs and link IDs
    file_ids = sorted([file.id for file in files]) if files else []
    link_ids = sorted([link.id for link in links]) if links else []

    # Generate an ID by joining all file and link IDs
    # Max is 63 Charected, we add "rag-chroma-" at the start
    retriever_id = ("_".join(file_ids + link_ids))[:52]

    # If no files or links, use "default"
    if not retriever_id:
        retriever_id = "default"

    return retriever_id

def conventional_ai_retriever(query: str, files=None, links=None) -> list[str]:
    # Get collection name
    retriever_id = get_retriever_id(files or [], links or [])
    collection_name = f"rag-chroma-{retriever_id}"

    embedding_function = SentenceTransformerEmbeddingFunction()
    chroma_client = get_chroma_client()
    chroma_collection = chroma_client.get_collection(collection_name, embedding_function=embedding_function)

    results = chroma_collection.query(query_texts=[query], n_results=5)
    return results['documents'][0]


def rag_ai_retriever(queries: list[str], files=None, links=None) -> list[str]:
    # Get collection name
    retriever_id = get_retriever_id(files or [], links or [])
    collection_name = f"rag-chroma-{retriever_id}"

    embedding_function = SentenceTransformerEmbeddingFunction()
    chroma_client = get_chroma_client()
    chroma_collection = chroma_client.get_collection(collection_name, embedding_function=embedding_function)

    results = chroma_collection.query(query_texts=queries, n_results=10, include=['documents', 'embeddings'])
    retrieved_documents = results['documents']

    unique_documents = set()
    for documents in retrieved_documents:
        for document in documents:
            unique_documents.add(document)

    unique_documents = list(unique_documents)
    original_query = queries[0]

    pairs = []
    for doc in unique_documents:
        pairs.append([queries[-1], doc])

    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    scores = cross_encoder.predict(pairs)

    ordered_list = []
    for o in np.argsort(scores)[::-1]:
        ordered_list.append(o)

    ranked_retrieved_documents =[]
    number_of_doc_needed = 15
    for i in range(number_of_doc_needed):
        ranked_retrieved_documents.append(pairs[ordered_list[i]][1])

    return ranked_retrieved_documents
