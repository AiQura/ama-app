
from graph.state import GraphState
from langchain_core.messages import BaseMessage, HumanMessage

from graph.chains.reflection import reflection_chain


def reflection_node(messages: list[BaseMessage])-> list[BaseMessage]:
    res = reflection_chain.invoke({"messages": messages})
    return  [HumanMessage(content=res.content)]

def reflect(state: GraphState) -> GraphState:
    print("---REFLECT---")

    results = reflection_node([HumanMessage(content=state['generation'])])
    state['reflection_result'] = results[0].content

    if 'reflection_index' not in state:
        state['reflection_index'] = 0
    state['reflection_index'] += 1

    print(f"-------------------------------------> REFLECTION ({state['reflection_index']}) <-------------------------------------")
    print(state['reflection_result'])
    print("--------------------------------------------------------------------------")

    return state
