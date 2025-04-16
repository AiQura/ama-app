
from typing import Dict, List, Any, Optional

from modules.file.file_model import FileModel
from modules.link.link_model import LinkModel
from utils.ai_utils import get_ai_client, conventional_ai_retriever

def run_conventional_query(query: str, files: Optional[List[FileModel]] = None,
                        links: Optional[List[LinkModel]] = None) -> Dict[str, Any]:
    """
    Process a query with the AI.

    Args:
        query: The user's query
        user_id: ID of the user making the query
        files: List of associated files
        links: List of associated links

    Returns:
        Dict: Result with thinking steps and response
    """
    thinking_steps = []

    openai_client = get_ai_client()
    model = "gpt-4o"

    retrieved_documents = conventional_ai_retriever(query, files, links)
    information = "\n\n".join(retrieved_documents)

    messages = [
        {
            "role": "user",
            "content": f"""Question: {query}

Information from document:
{information}
"""
        }
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,  # Add some creativity while keeping responses focused
        max_tokens=10000   # Adjust based on your needs
    )
    content = response.choices[0].message.content

    return {
        "question": query,
        "answer": content,
        "events": thinking_steps
    }
