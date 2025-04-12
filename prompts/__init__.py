"""
Prompts used with OpenAI
"""

from prompts.ai_query import run_ai_query
from prompts.rag_query import run_rag_query

__all__ = [
    "run_rag_query",
    "run_ai_query",
]
