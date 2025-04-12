from typing import List, TypedDict, Optional, Any


class GraphState(TypedDict, total=False):
    """
    Represents the state of our graph.

    Attributes:
        question: user's question
        generation: LLM generation/answer
        web_search: whether to add web search
        documents: list of retrieved documents
        files: list of selected files
        links: list of selected links
    """

    question: str
    generation: Optional[str]
    web_search: bool
    documents: List[Any]
    files: List[Any]
    links: List[Any]
