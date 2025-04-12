from langchain import hub
from langchain_core.output_parsers import StrOutputParser

from langgraph_integration.model_config import get_default_model

llm = get_default_model()
prompt = hub.pull("rlm/rag-prompt")

generation_chain = prompt | llm | StrOutputParser()
