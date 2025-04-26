def spare_parst_extractor(query, model="gpt-4o"):
    messages = [
        {
            "role": "system",
            "content": """You are a helpful expert Data analysis team lead . you will get an answer that may or may not contains Spare parts numbers, the answer contains alot of data so do the following . "
            "if the answer contains the spare parts numbers, you have to extract the parts names and the parts numbers along with the brand name and equipment type, the return has to be in a shape of question for the price. "
            "if the answer does not contain part numbers but contains brand name or type of equipment, return back ' No part numbers available'.
            
            Question: [add the question here after rephrasing it as mentioned above]
            
            """
        },
        {"role": "user", "content": query}
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = response.choices[0].message.content
    # content = content.split("\n")
    graphstate= GraphState()
    graphstate["spare_parts_generation"] = content
    return content