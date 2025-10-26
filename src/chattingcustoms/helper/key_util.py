"""Utility Function to Handle all API key"""

import os
from dotenv import load_dotenv
from helper import file_util
import streamlit as st

def return_open_api_key():
    """Return OpenAI API Key from Streamlit secrets or fallback to .env"""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except KeyError:
        st.warning("OPENAI_API_KEY not found in secrets.toml, trying .env files")
        load_dotenv()
        environment = os.getenv("environment")
        print(environment)
        script_directory = os.path.dirname(os.path.abspath(__file__))

        print(script_directory)
        dotenv_path = file_util.find_file_in_parent_directories(environment + ".env", script_directory)
        print(dotenv_path)
        load_dotenv(dotenv_path)
        return os.getenv("OPENAI_API_KEY")
    