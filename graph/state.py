from typing import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        retriever_id: The id used to fetch the correct collection
        question: question
        generation: LLM generation
        spare_parts_generation: whether to search for the price or not
        web_search: whether to add search
        documents: list of documents
        price_documents: list of documents
    """

    retriever_id: str
    question: str
    generation: str
    spare_parts_generation: str
    web_search: bool
    documents: list[str]
    price_documents: list[str]
