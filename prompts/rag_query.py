
import traceback
from utils.ai_utils import get_ai_client, rag_ai_retriever

def augment_multiple_query(query, model="gpt-3.5-turbo"):
    openai_client = get_ai_client()
    messages = [
        {
            "role": "system",
            "content": "You are a helpful expert Maintenance team lead . Your users are asking questions about information contained in an Attached maintenance manual. "
            "Suggest up to 8 additional related questions to help them find the information they need, for the provided question. the last one of the questions has to ask about a step by step solution."
            "Suggest only short questions without compound sentences, between 8 to 15 words. Suggest a variety of questions that cover different aspects of the topic."
            "Make sure they are complete questions, and that they are related to the original question."
            "Output one question per line. Do not number the questions."
        },
        {"role": "user", "content": query}
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = response.choices[0].message.content
    content = content.split("\n")
    return content

def rag4o(query, retrieved_documents, model="gpt-4o"):
    openai_client = get_ai_client()
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
            [Your detailed answer based only on the provided information, along with the part number needed, AND the PART NUMBER IS A MUST WHATEVER PART MENTIONED IN THE ANSWER YOU NEED TO MENTION ITS PART NUMBER]

            Part Numbers:
            [Mention every part number for whatever parts you  mentioned in your answer or thoughts, if one of the parts does not have a part number mention it does not have and mention any data for that part which is available in the manual]

            """
        },
        {
            "role": "user",
            "content": f"""Question: {query}

Information from document:
{information}

Please provide your thought process and final answer."""
        }
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,  # Add some creativity while keeping responses focused
        max_tokens=10000   # Adjust based on your needs
    )
    content = response.choices[0].message.content
    return content

def run_rag_query(original_query: str, files=None, links=None) -> dict:
    """
    Run a query through the LangGraph system

    Args:
        question: The user's question
        files: List of file models to include (optional)
        links: List of link models to include (optional)

    Returns:
        dict: The final state with the answer
    """
    try:
        augmented_queries = augment_multiple_query(original_query)
        queries = [original_query] + augmented_queries

        ranked_retrieved_documents = rag_ai_retriever(queries, files, links)
        ranked_results = rag4o(queries[-1], ranked_retrieved_documents)

        return {
            "question": original_query,
            "answer": ranked_results,
            "events": []
        }
    except Exception as e:
        error_message = str(e)
        print(traceback.format_exc())

        return {
            "question": original_query,
            "answer": f"Error processing query: {error_message}",
            "events": ["Error: " + error_message]
        }

