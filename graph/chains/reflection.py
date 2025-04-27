from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

REFLECTION_END_ANSWER = 'useful answer'.lower()

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",f"""you are a maintenance technical manager. Generate critique and recommendations for the answer that you will receive, the critique or the recommendation has to follow the following instructions:
         1 - does the answer has the following section (thought process, Final Answer, Brand name, Part Numbers ), if yes continue to next point. if no, ask the model to provide the answer again containing what is missing.
         2 - critique the thought process section, if you found it good continue to next point. if not, recommend what to modify, and continue to next point.
         3 - critique the Final Answer section, if you found it good continue to next point. if not, recommend what to modify, and continue to next point.
         4 - did the Brand name section contain the brand name, if yes don,t critiqe or recommend and continue to next point. If not mentioned, ask if it is available in the manual, and if you recived not available in manual dont recommend or critique and continue to next point.
         5 - ask if the Part Numbers section contain all the spare part numbers needed to solve the problem, if you recieved somthing like yes those all the part numbers you need it okay critique is done.

        if all of the above comments are Okay and available dont critique or recommend, only return '{REFLECTION_END_ANSWER}' """),
        MessagesPlaceholder(variable_name="messages")
    ]
    )


llm = ChatOpenAI()
reflection_chain = reflection_prompt | llm
