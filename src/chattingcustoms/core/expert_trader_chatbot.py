from helper import prompt_util

def chatting_with_expert_trader(user_query:str):
    system_message = f"""

    I am an expert Trader that has experience helping in import and export declaration.
    my `query` will be enclosed in <incoming-message></incoming-message> the user message.  
    I am doing it in Singapore and please provide reference website

    return in query in markdown text with summarize answers
    """
    messages =  [
    {'role':'system',
    'content': system_message},
    {'role':'user',
    'content': f"<incoming-message>{user_query}</incoming-message>"},
    ]

    return prompt_util.get_completion_from_messages(messages)
    