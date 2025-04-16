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

from langgraph_integration.ingestion import _get_retriever_id, get_retriever

@st.cache_resource
def get_ai_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@st.cache_resource
def get_chroma_client():
    return chromadb.Client()


def retrieve_documents(query: str, files=None, links=None) -> list[str]:
    retriever = get_retriever(files if files is not None else [
    ], links if links is not None else [])

    documents = retriever.invoke(query)
    return [doc.page_content for doc in documents]

def conventional_ai_retriever(query: str, files=None, links=None) -> list[str]:
    # Get collection name
    retriever_id = _get_retriever_id(files or [], links or [])
    collection_name = f"rag-chroma-{retriever_id}"

    embedding_function = SentenceTransformerEmbeddingFunction()
    chroma_client = get_chroma_client()
    chroma_collection = chroma_client.get_collection(collection_name, embedding_function=embedding_function)

    results = chroma_collection.query(query_texts=[query], n_results=5)
    return results['documents'][0]


def rag_ai_retriever(queries: list[str], files=None, links=None) -> list[str]:
    # Get collection name
    retriever_id = _get_retriever_id(files or [], links or [])
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
