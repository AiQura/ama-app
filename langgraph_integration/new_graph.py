import os
from openai import OpenAI
from langgraph_integration.ingestion import get_retriever


def get_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def rag(query: str, retrieved_documents: list[str], model="chatgpt-4o-latest"):
    information = "\n\n".join(retrieved_documents)

    messages = [
        {
            "role": "system",
            "content": """You are a helpful expert Maintenance team lead . Your users are asking questions about information contained in an Attached maintenance manual.
            Follow these steps:
            1. First, analyze the question carefully
            2. Review the provided information from the the attached maintenance manual by starting with the table of content if available and take it as an entry point to the sections of the manual.
            3. if the table of content is not available, then review the manual from the beginning to the end befor answering.
            4. If the question is not related to the maintenance manual, ask the user to provide a more specific question.
            5. If answer seems to be in manual, Think step by step about how to answer the question
            6. Provide your final answer based on the information
            7. If the answer is not found in the manual, then ask the user to provide a more specific question.
            8. make the answer as detailed as possible so a non technical person can under stand it but also use technical terms drawen from the manual.
            9. If a part is reuired to fix the problem and you suggest to change it, then provide the part number and for each part, a part number has to be mentioned.
            Format your response as:
            
            Thought Process:
            - [Your step by step reasoning]
            
            Final Answer:
            [Your detailed answer based only on the provided information, along with the part number needed, AND THIS IS A MUST WHATEVER PART MENTIONED NEEDS TO HAVE A PART NUMBER]"""
        },
        {
            "role": "user",
            "content": f"""Question: {query}

Information from document:
{information}

Please provide your thought process and final answer."""
        }
    ]

    openai_client = get_client()
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,  # Add some creativity while keeping responses focused
        # Adjust based on your needs (Max tokens for gtp-3.5 is 4096)
        max_tokens=10000
    )
    content = response.choices[0].message.content
    return content


def retrieve_documents(query: str, files=None, links=None) -> list[str]:
    retriever = get_retriever(files if files is not None else [
    ], links if links is not None else [])

    documents = retriever.invoke(query)
    return [doc.page_content for doc in documents]


def run_new_query(question: str, files=None, links=None) -> dict:
    """
    Run a query through the LangGraph system

    Args:
        question: The user's question
        files: List of file models to include (optional)
        links: List of link models to include (optional)

    Returns:
        dict: The final state with the answer
    """
    # model = "gpt-3.5-turbo-16k"
    model = "chatgpt-4o-latest"

    try:
        # First iteration
        first_documents = retrieve_documents(question, files, links)
        hypothetical_answer = rag(
            query=question, retrieved_documents=first_documents, model=model)

        # Second iteration
        joint_query = f"{question} \n {hypothetical_answer}"
        last_documents = retrieve_documents(joint_query, files, links)
        final_answer = rag(
            query=question, retrieved_documents=last_documents, model=model)

        return {
            "question": question,
            "answer": final_answer,
            "events": []
        }
    except Exception as e:
        error_message = str(e)
        return {
            "question": question,
            "answer": f"Error processing query: {error_message}",
            "events": ["Error: " + error_message]
        }
