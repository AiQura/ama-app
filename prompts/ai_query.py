
from typing import Dict, List, Any, Optional

from models.file_model import FileModel
from models.link_model import LinkModel
from utils.ai_utils import get_ai_client, retrieve_documents

def run_ai_query(query: str, files: Optional[List[FileModel]] = None,
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
    # In a real implementation, this would call an external AI service or API
    # For now, we'll simulate the AI response

    thinking_steps = []

    openai_client = get_ai_client()
    model = "chatgpt-4o-latest"

    retrieved_documents = retrieve_documents(query, files, links)
    information = "\n\n".join(retrieved_documents)

    ai_response = openai_client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": f"""Question: {query}

Information from document:
{information}
            """
        }],
        temperature=0.1,  # Add some creativity while keeping responses focused
        # Adjust based on your needs (Max tokens for gtp-3.5 is 4096)
        max_tokens=10000
    )
    response = ai_response.choices[0].message.content

    return {
        "question": query,
        "answer": response,
        "events": thinking_steps
    }
