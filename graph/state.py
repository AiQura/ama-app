from typing import List, TypedDict , Any, Dict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        spare_parts_generation: whether to search for the price or not
        web_search: whether to add search
        documents: list of documents
        price_documents: list of documents
    """

    question: str
    generation: str
    spare_parts_generation: str
    web_search: bool
    documents: List[str]
    price_documents: List[str]