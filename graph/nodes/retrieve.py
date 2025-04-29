from graph.state import GraphState
from prompts.rag_query import augment_multiple_query
from utils.ai_utils import rag_ai_retriever


def retrieve(state: GraphState) -> GraphState:
    print("---RETRIEVE---")
    question = state["question"]
    retriever_id = state["retriever_id"]

    augmented_queries = augment_multiple_query(question)
    queries = [question] + augmented_queries

    ranked_retrieved_documents = rag_ai_retriever(queries, retriever_id)
    return {"documents": ranked_retrieved_documents, "question": question}
