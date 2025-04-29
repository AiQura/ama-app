
from graph.state import GraphState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from graph.chains.spare_parts_extraction import spare_parts_extraction_chain


def spare_parts_extraction_node(messages: list[BaseMessage])-> list[BaseMessage]:
    res = spare_parts_extraction_chain.invoke({"messages": messages})
    return  [AIMessage(content=res.content)]

def extract_spare_parts(state: GraphState) -> GraphState:
    print("---REFLECT---")

    results = spare_parts_extraction_node([HumanMessage(content=state['generation'])])
    state['spare_parts_generation'] = results[0].content

    print(f"-------------------------------------> SPARE PARTS EXTRACTION <-------------------------------------")
    print(state['spare_parts_generation'])
    print("--------------------------------------------------------------------------")

    return state
