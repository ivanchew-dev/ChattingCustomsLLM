from helper import prompt_util

def chatting_with_self_service_trader(user_query:str):
    system_message = f"""

    I have never imported or exported any goods before in Singapore.  Please provide instructions in step by step
    information as well as reference websites.
    my `query` will be enclosed in <incoming-message></incoming-message> the user message.

     return in markdown text with line feed and breakdown with subheadings
    """
    #return in Json format only.  main key :chattingcustoms. sub keys :trader_category, answer
    
    messages =  [
    {'role':'system',
    'content': system_message},
    {'role':'user',
    'content': f"<incoming-message>{user_query}</incoming-message>"},
    ]

    return prompt_util.get_completion_from_messages(messages)
    