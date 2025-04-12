"""
Node for web search functionality.
"""
from typing import Any, Dict, List, Optional
import os
import streamlit as st

from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph_integration.state import GraphState

# Mock web search for when Tavily is not available
def mock_web_search(query: str) -> List[Dict[str, str]]:
    """Create a mock web search result for when Tavily is not available"""
    return [
        {
            "content": f"This is a mock search result for: '{query}'. "
                      f"To enable real web search, please add your Tavily API key in the sidebar."
        },
        {
            "content": "Web search results would normally appear here with information from the internet."
        }
    ]

# Initialize web search tool - lazy load to avoid API key issues
_web_search_tool = None

def get_web_search_tool():
    """Get or initialize the web search tool"""
    global _web_search_tool

    if _web_search_tool is not None:
        return _web_search_tool

    # Check for API key
    tavily_api_key = os.environ.get("TAVILY_API_KEY")

    try:
        if tavily_api_key:
            _web_search_tool = TavilySearchResults(k=3)
        else:
            print("Warning: TAVILY_API_KEY not set. Using mock web search.")

            # Create a mock tool with the same interface
            class MockTavilySearch:
                def invoke(self, query_dict):
                    return mock_web_search(query_dict["query"])

            _web_search_tool = MockTavilySearch()

    except Exception as e:
        print(f"Error initializing Tavily search: {e}")

        # Fallback mock implementation
        class MockTavilySearch:
            def invoke(self, query_dict):
                return mock_web_search(query_dict["query"])

        _web_search_tool = MockTavilySearch()

    return _web_search_tool


def web_search(state: GraphState) -> Dict[str, Any]:
    """
    Perform a web search for the query.

    Args:
        state: The current graph state

    Returns:
        Updated state with web search results added to documents
    """
    print("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents", [])

    # Get files and links from the state
    files = state.get("files", [])
    links = state.get("links", [])

    # Get or initialize the web search tool
    web_search_tool = get_web_search_tool()

    try:
        # Perform web search
        search_results = web_search_tool.invoke({"query": question})
        web_results = "\n".join([d["content"] for d in search_results])
        web_results_doc = Document(page_content=web_results, metadata={"source": "web_search"})

        # Add to documents
        if documents:
            documents.append(web_results_doc)
        else:
            documents = [web_results_doc]
    except Exception as e:
        print(f"Error during web search: {e}")
        # Create a fallback document if web search fails
        error_doc = Document(
            page_content=f"Web search failed with error: {str(e)}",
            metadata={"source": "web_search_error"}
        )
        if documents:
            documents.append(error_doc)
        else:
            documents = [error_doc]

    return {
        "documents": documents,
        "question": question,
        "files": files,
        "links": links
    }
