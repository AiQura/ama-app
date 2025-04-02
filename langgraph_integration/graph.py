import os
import streamlit as st
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from langgraph_integration.chains.answer_grader import answer_grader
from langgraph_integration.chains.hallucination_grader import hallucination_grader
from langgraph_integration.chains.router import question_router, RouteQuery
from langgraph_integration.consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH
from langgraph_integration.nodes import generate, grade_documents, retrieve, web_search
from langgraph_integration.state import GraphState

# In-memory state for tracking graph execution
memory = MemorySaver()

# Track all events that happen during execution for display
trace_events = []

def log_event(message):
    """Log an event to the trace events list"""
    trace_events.append(message)
    print(message)

def clear_events():
    """Clear all events"""
    trace_events.clear()

def get_events():
    """Get all logged events"""
    return trace_events


def decide_to_generate(state):
    log_event("---ASSESS GRADED DOCUMENTS---")

    if state["web_search"]:
        log_event("---DECISION: NOT ALL DOCUMENTS ARE RELEVANT TO QUESTION, INCLUDE WEB SEARCH---")
        return WEBSEARCH
    else:
        log_event("---DECISION: GENERATE---")
        return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    log_event("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if hallucination_grade := score.binary_score:
        log_event("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        log_event("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            log_event("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            log_event("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        log_event("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


def route_question(state: GraphState) -> str:
    log_event("---ROUTE QUESTION---")
    question = state["question"]
    source: RouteQuery = question_router.invoke({"question": question})
    if source.datasource == WEBSEARCH:
        log_event("---ROUTE QUESTION TO WEB SEARCH---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        log_event("---ROUTE QUESTION TO RAG---")
        return RETRIEVE


def check_api_key():
    """Check if OpenAI API key is available"""
    return "OPENAI_API_KEY" in os.environ


# Main workflow graph
workflow = None

def build_graph():
    """
    Build and return the workflow graph
    
    Returns:
        The compiled workflow or None if API key not available
    """
    if not check_api_key():
        return None
        
    try:
        workflow = StateGraph(GraphState)
        workflow.add_node(RETRIEVE, retrieve)
        workflow.add_node(GRADE_DOCUMENTS, grade_documents)
        workflow.add_node(GENERATE, generate)
        workflow.add_node(WEBSEARCH, web_search)

        workflow.set_conditional_entry_point(
            route_question,
            {
                WEBSEARCH: WEBSEARCH,
                RETRIEVE: RETRIEVE,
            },
        )
        workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
        workflow.add_conditional_edges(
            GRADE_DOCUMENTS,
            decide_to_generate,
            {
                WEBSEARCH: WEBSEARCH,
                GENERATE: GENERATE,
            },
        )
        workflow.add_edge(WEBSEARCH, GENERATE)
        workflow.add_conditional_edges(
            GENERATE,
            grade_generation_grounded_in_documents_and_question,
            {
                "not supported": GENERATE,
                "useful": END,
                "not useful": WEBSEARCH,
            },
        )

        return workflow.compile(checkpointer=memory)
    except Exception as e:
        print(f"Error building graph: {e}")
        return None


def get_app():
    """Get or build the graph app"""
    global workflow
    if workflow is None:
        workflow = build_graph()
    return workflow


def run_query(question: str, files=None, links=None) -> dict:
    """
    Run a query through the LangGraph system
    
    Args:
        question: The user's question
        files: List of file models to include (optional)
        links: List of link models to include (optional)
        
    Returns:
        dict: The final state with the answer
    """
    clear_events()
    app = get_app()
    
    if app is None:
        return {
            "question": question,
            "answer": "Error: OpenAI API key is required to use LangGraph RAG. Please add your API key in the sidebar.",
            "events": ["Error: OpenAI API key is missing"]
        }
    
    try:
        # Initialize inputs with question and selected files/links
        inputs = {
            "question": question,
            "files": files or [],
            "links": links or []
        }
        
        # Generate a unique thread ID for this query using a timestamp
        import time
        thread_id = f"thread_{int(time.time())}"
        
        final_output = None
        # Run the graph and collect all outputs
        for output in app.stream(inputs, config={"configurable": {"thread_id": thread_id}}):
            for key, value in output.items():
                # Keep the final state
                final_output = value
        
        result = {
            "question": question,
            "answer": final_output["generation"] if final_output and "generation" in final_output else "No answer generated",
            "events": get_events()
        }
        
        return result
    except Exception as e:
        error_message = str(e)
        return {
            "question": question,
            "answer": f"Error processing query: {error_message}",
            "events": ["Error: " + error_message]
        }