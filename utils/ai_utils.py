"""
OpenAI utils
"""

import os
from openai import OpenAI

from langgraph_integration.ingestion import get_retriever

def get_ai_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def retrieve_documents(query: str, files=None, links=None) -> list[str]:
    retriever = get_retriever(files if files is not None else [
    ], links if links is not None else [])

    documents = retriever.invoke(query)
    return [doc.page_content for doc in documents]
