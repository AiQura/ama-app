from langgraph.graph import END, StateGraph, START

from graph.chains.reflection import REFLECTION_END_ANSWER
from graph.chains.spare_parts_extraction import SPARE_PARTS_EXTRACTION_END_ANSWER
from graph.consts import EXTRACT_SPARE_PARTS, GENERATE, REFLECT, RETRIEVE_AND_GRADE, WEBSEARCH
from graph.nodes.extract_spare_parts import extract_spare_parts
from graph.nodes.generate import generate
from graph.nodes.reflect import reflect
from graph.nodes.retrieve import retrieve
from graph.nodes.web_search import web_search
from graph.state import GraphState

def reflection_decision_maker(state) -> str:
    print("---ASSESS REFLECTION OUTPUT---")

    if REFLECTION_END_ANSWER in state["reflection_result"].lower() or state["reflection_index"] > 3:
        print(
            "---DECISION: USEFUL ANSWER, EXTRACT SPARE PARTS---"
        )
        return EXTRACT_SPARE_PARTS
    else:
        print("---DECISION: GENERATE---")
        return GENERATE

def spare_parts_extraction_decision_maker(state) -> str:
    print("---ASSESS EXTRACT_SPARE_PARTS OUTPUT---")

    if SPARE_PARTS_EXTRACTION_END_ANSWER in state["spare_parts_generation"].lower():
        print(
            "---DECISION: NO PARTS AVAILABLE, END---"
        )
        return END
    else:
        print("---DECISION: WEBSEARCH---")
        return WEBSEARCH


def get_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node(RETRIEVE_AND_GRADE, retrieve)
    workflow.add_node(GENERATE, generate)
    workflow.add_node(REFLECT, reflect)
    workflow.add_node(EXTRACT_SPARE_PARTS, extract_spare_parts)
    workflow.add_node(WEBSEARCH, web_search)


    workflow.add_edge(START, RETRIEVE_AND_GRADE)
    workflow.add_edge(RETRIEVE_AND_GRADE, GENERATE)
    workflow.add_edge(GENERATE, REFLECT)
    workflow.add_conditional_edges(
        REFLECT,
        reflection_decision_maker,
        {
            EXTRACT_SPARE_PARTS: EXTRACT_SPARE_PARTS,
            GENERATE: GENERATE,
        },
    )
    workflow.add_conditional_edges(
        EXTRACT_SPARE_PARTS,
        spare_parts_extraction_decision_maker,
        {
            END: END,
            WEBSEARCH: WEBSEARCH,
        },
    )
    workflow.add_edge(WEBSEARCH, END)


    app = workflow.compile()
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    return app
