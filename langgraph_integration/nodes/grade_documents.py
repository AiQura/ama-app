"""
Node for grading document relevance.
"""
from typing import Any, Dict, List

from langchain.schema import Document
from langgraph_integration.chains.retrieval_grader import retrieval_grader
from langgraph_integration.state import GraphState


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question.
    If any document is not relevant, we will set a flag to run web search.

    Args:
        state: The current graph state

    Returns:
        Updated state with filtered documents and web_search flag
    """
    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]
    
    # Get files and links from the state
    files = state.get("files", [])
    links = state.get("links", [])
    
    # Handle case where no documents were retrieved
    if not documents:
        print("---NO DOCUMENTS RETRIEVED, USING WEB SEARCH---")
        return {
            "documents": [], 
            "question": question, 
            "web_search": True,
            "files": files,
            "links": links
        }

    filtered_docs: List[Document] = []
    web_search = False
    
    for d in documents:
        try:
            score = retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score.binary_score
            if grade.lower() == "yes":
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
                web_search = True
                continue
        except Exception as e:
            print(f"Error grading document: {e}")
            web_search = True
            
    return {
        "documents": filtered_docs, 
        "question": question, 
        "web_search": web_search,
        "files": files,
        "links": links
    }