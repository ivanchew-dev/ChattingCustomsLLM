
from openai import OpenAI
from helper import key_util

# This is the "Updated" helper function for calling LLM
ApiKey = key_util.return_open_api_key()

# This a "modified" helper function that we will discuss in this session
# Note that this function directly take in "messages" as the parameter.
def get_completion_from_messages( messages, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1):
    client = OpenAI(api_key=ApiKey)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        n=n
    )
    return response.choices[0].message.content


