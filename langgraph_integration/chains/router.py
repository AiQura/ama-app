from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from langgraph_integration.model_config import get_structured_output_model


# class RouteQuery(BaseModel):
#     """Route a user query to the most relevant datasource."""

#     datasource: Literal["vectorstore", "websearch"] = Field(
#         ...,
#         description="Given a user question choose to route it to web search or a vectorstore.",
#     )

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore"] = Field(
        ...,
        description="Given a user question choose to go to vectorstore.",
    )


llm = get_structured_output_model()
structured_llm_router = llm.with_structured_output(RouteQuery)

system = """You are an expert at routing a user question to a vectorstore or web search.
The vectorstore contains documents related to agents, prompt engineering, and adversarial attacks.
Use the vectorstore for questions on these topics. For all else, use web-search."""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = structured_llm_router