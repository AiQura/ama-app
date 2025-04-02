"""
Node for retrieving documents from vector store.
"""
from typing import Any, Dict, List, Optional

from langgraph_integration.ingestion import get_retriever
from langgraph_integration.state import GraphState


def retrieve(state: GraphState) -> Dict[str, Any]:
    """
    Retrieve documents from the vector store.
    
    Args:
        state: The current graph state
        
    Returns:
        Updated state with retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]
    
    # Get files and links from the state
    files = state.get("files", [])
    links = state.get("links", [])
    
    # Get retriever based on selected files and links
    retriever = get_retriever(files, links)
    
    if retriever is None:
        # Return empty documents if retriever is not available
        return {"documents": [], "question": question, "files": files, "links": links}
    
    # Retrieve documents based on the question
    documents = retriever.invoke(question)
    
    return {
        "documents": documents, 
        "question": question,
        "files": files,
        "links": links
    }