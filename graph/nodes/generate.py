
from graph.state import GraphState
from prompts.rag_query import rag4o


def generate(state: GraphState) -> GraphState:
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    generation = rag4o(question, documents)
    return {"documents": documents, "question": question, "generation": generation}
