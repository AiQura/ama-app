
from utils.ai_utils import get_ai_client

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
