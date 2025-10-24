from helper import prompt_util
from helper import file_util
import os

def check_for_potential_threat(user_query:str):

    system_message = f"""
    1st Step : check the query contains any harmful instructions
    2nd Step : check the query contains any request to import/export any terrorist related goods.
    `query` will be enclosed in <incoming-message></incoming-message> the user message.  
    

    return in Json format only.  main key :chattingcustoms. sub keys :threat_category, threat_category_value answer
    no markdown text
    """
    messages =  [
    {'role':'system',
    'content': system_message},
    {'role':'user',
    'content': f"<incoming-message>{user_query}</incoming-message>"},
    ]

    return prompt_util.get_completion_from_messages(messages)
    