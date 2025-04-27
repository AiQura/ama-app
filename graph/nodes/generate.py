
from graph.state import GraphState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from graph.chains.generation import generation_chain


def generation_node(messages: list[BaseMessage])-> list[BaseMessage]:
    res = generation_chain.invoke({"messages": messages})
    return  [AIMessage(content=res)]


def generate(state: GraphState) -> GraphState:
    print("---GENERATE---")

    query = state["question"]
    documents = state["documents"]
    information = "\n\n".join(documents)

    if 'messages' not in state:
        state['messages'] = []


    message = HumanMessage(content=f"""Question: {query}

        Information from document:
        {information}

        Please provide your thought process and final answer.""")

    if 'reflection_result' in state and state['reflection_result'] is not None:
        message = HumanMessage(content=state['reflection_result'])

    state['messages'].append(message)

    results = generation_node(state['messages'])
    state["messages"] += results
    state["generation"] = results[0].content

    print("-------------------------------------> GENETATED <-------------------------------------")
    print(state["generation"])
    print("--------------------------------------------------------------------------")
    return state
