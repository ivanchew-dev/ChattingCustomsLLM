"""Utility Function to Handle all API key"""

import os
from dotenv import load_dotenv
from helper import file_util


def return_open_api_key():
    load_dotenv()
    environment = os.getenv("environment")
    print(environment)
    script_directory = os.path.dirname(os.path.abspath(__file__))

    print(script_directory)
    dotenv_path= file_util.find_file_in_parent_directories(environment + ".env",script_directory)
    print(dotenv_path)
    load_dotenv(dotenv_path)
    return os.getenv("OPENAI_API_KEY")