"""
Node for generating answers.
"""
from typing import Any, Dict

from langgraph_integration.chains.generation import generation_chain
from langgraph_integration.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    """
    Generate an answer from the retrieved documents and question.

    Args:
        state: The current graph state

    Returns:
        Updated state with the generated answer
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # Get files and links from the state
    files = state.get("files", [])
    links = state.get("links", [])

    generation = generation_chain.invoke({"context": documents, "question": question})

    return {
        "documents": documents,
        "question": question,
        "generation": generation,
        "files": files,
        "links": links
    }
