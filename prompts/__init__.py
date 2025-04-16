"""
Prompts used with OpenAI
"""

from prompts.conventional_query import run_conventional_query
from prompts.rag_query import run_rag_query

__all__ = [
    "run_rag_query",
    "run_conventional_query",
]
