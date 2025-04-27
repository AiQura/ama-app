from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

SPARE_PARTS_EXTRACTION_END_ANSWER = 'No part numbers available'.lower()

spare_parts_extraction_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",F"""You are a helpful expert Data analysis team lead . you will get an answer that may or may not contains Spare parts numbers, the answer contains alot of data so do the following . "
            "if the answer contains the spare parts numbers, you have to extract the parts names and the parts numbers along with the brand name and equipment type, the return has to be in a shape of question for the price. "
            "if the answer does not contain part numbers but contains brand name or type of equipment, return back '{SPARE_PARTS_EXTRACTION_END_ANSWER}'.
            "the lenght has to be 350 charachter as MAX."

            Question: [add the question here after rephrasing it as mentioned above]

            """),
        MessagesPlaceholder(variable_name="messages")
    ]
    )


llm = ChatOpenAI()
spare_parts_extraction_chain = spare_parts_extraction_prompt | llm
