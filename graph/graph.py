from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START

from graph.chains.answer_grader import answer_grader
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.reflection import REFLECTION_END_ANSWER
from graph.chains.router import question_router, RouteQuery
from graph.consts import EXTRACT_SPARE_PARTS, GENERATE, REFLECT, RETRIEVE_AND_GRADE, WEBSEARCH
from graph.nodes.generate import generate
from graph.nodes.reflect import reflect
from graph.nodes.retrieve import retrieve
from graph.state import GraphState



def reflection_decision_maker(state):
    print("---ASSESS REFLECTION OUTPUT---")

    if REFLECTION_END_ANSWER in state["reflection_result"].lower() or state["reflection_index"] > 3:
        print(
            "---DECISION: USEFUL ANSWER, END---"
        )
        return END
    else:
        print("---DECISION: GENERATE---")
        return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


def route_question(state: GraphState) -> str:
    print("---ROUTE QUESTION---")
    question = state["question"]
    source: RouteQuery = question_router.invoke({"question": question})
    if source.datasource == WEBSEARCH:
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return RETRIEVE_AND_GRADE

def get_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node(RETRIEVE_AND_GRADE, retrieve)
    workflow.add_node(GENERATE, generate)
    workflow.add_node(REFLECT, reflect)
    # workflow.add_node(EXTRACT_SPARE_PARTS,)
    # workflow.add_node(WEBSEARCH, web_search)


    workflow.add_edge(START, RETRIEVE_AND_GRADE)
    workflow.add_edge(RETRIEVE_AND_GRADE, GENERATE)
    workflow.add_edge(GENERATE, REFLECT)
    workflow.add_conditional_edges(
        REFLECT,
        reflection_decision_maker,
        {
            END: END,
            GENERATE: GENERATE,
        },
    )
    # workflow.add_edge(REFLECT, END)
    # workflow.add_conditional_edges(
    #     GENERATE,
    #     grade_generation_grounded_in_documents_and_question,
    #     {
    #         "not supported": GENERATE,
    #         "useful": END,
    #         "not useful": WEBSEARCH,
    #     },
    # )


    # memory = MemorySaver()
    # return workflow.compile(checkpointer=memory)
    return workflow.compile()

    # inputs = {"question": "Hello, how are you?", "retriever_id": "123"}
    # result = app.invoke(inputs)

    # app.get_graph().draw_mermaid_png(output_file_path="graph.png")
