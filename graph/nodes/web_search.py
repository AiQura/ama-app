from langchain.schema import Document
from langchain_tavily import TavilySearch

from graph.state import GraphState

web_search_tool = TavilySearch(max_results=5)


def web_search(state: GraphState) -> GraphState:
    print("---WEB SEARCH---")
    question = state["spare_parts_generation"]

    result_of_search = web_search_tool.invoke({"query": question})

    if 'price_documents' not in state:
        state['price_documents'] = []

    if 'error' in result_of_search:
        raise result_of_search["error"]
    
    for result in result_of_search["results"]:
        state['price_documents'].append(
            f"{result['url']} : {result['content']}")

    prices_information = "\n\n".join(state['price_documents'])

    state["generation"] += f"\n\n\n\n{prices_information}"

    print(f"-------------------------------------> WEB SEARCH <-------------------------------------")
    print(prices_information)
    print("--------------------------------------------------------------------------")

    return state
