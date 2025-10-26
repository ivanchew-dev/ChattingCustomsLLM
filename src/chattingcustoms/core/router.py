
from helper import prompt_util
from helper import file_util
from helper import network_util
from helper import geo_location_util
from core import expert_trader_chatbot
from core import self_service_trader_chatbot
from core import threat_assessment_chatbot
from core import tno_chatbot

import json
import datetime

import streamlit as st

def trader_categorizer(user_query):
    system_prompt_categorizer = """\
Categorize the query into one of the following categories:
- 'Self Service Trader': If the user is asking about general questions on how to import or export goods in Singapore. User has limited knowledge on import and export.
- 'Expert Trader': If the user is asking about detailed and in-depth queries on how to import or export goods in Singapore. User has in-depth knowledge on import and export processes.
- 'Other': If the user's query doesn't fall into any of the above categories.

The `query` will be enclosed in <incoming-message></incoming-message> the user message.

Format answer in plain text
"""


    messages = [
        {'role': 'system', 'content': system_prompt_categorizer},
        {'role': 'user', 'content': f"<incoming-message>I am enquiring about import into Singapore. {user_query}</incoming-message>"}
    ]

    return prompt_util.get_completion_from_messages(messages)

def route_to_chatbot(user_query:str):
    trader_category = trader_categorizer(user_query)
    st.write("Before threat assessment")
    threat_assessment = json.loads(threat_assessment_chatbot.check_for_potential_threat(user_query))
    st.write (threat_assessment)
    st.write(type(threat_assessment))
    st.write(threat_assessment.keys())
    st.write(threat_assessment['chattingcustoms']['threat_category'])
    st.write("Trader Category : ", trader_category)
    
    # Check if user is logged in (customs officer)
    if st.session_state.get("password_correct", False):
        trader_category = "customs_officer"
        st.write(trader_category)
    st.write("After threat assessment")
    st.write("Trader Category : ", trader_category)
    
    if (threat_assessment['chattingcustoms']['threat_category'].lower() == "none"):
        if trader_category.casefold() == 'expert trader':
            return expert_trader_chatbot.chatting_with_expert_trader(user_query)
        elif trader_category.casefold() == 'self service trader':
            return self_service_trader_chatbot.chatting_with_self_service_trader(user_query)
        elif trader_category.casefold() == 'customs_officer':
            return tno_chatbot.rule_enquiry(user_query)
        else:
            return 'We are unable to answer your query as it is not related to import and export'
    else:
        # Handle threat detected - log the incident
        st.write("Logging Threatening Query...")
        
        ip_address = network_util.get_public_ip()
        st.write("IP Address: ", ip_address)
        st.stop()
        lat_log = geo_location_util.get_location_from_ip_local(ip_address)
        latitude = lat_log[0]
        longitude = lat_log[1]
        st.write("Latitude: ", latitude)
        st.write("Longitude: ", longitude)
        # Get username safely
        username = st.session_state.get("username", "anonymous")
        st.write("Username: ", username)
        st.stop()
        data_row = [
            user_query, ip_address, latitude, longitude,
            threat_assessment['chattingcustoms']['threat_category'], 
            threat_assessment['chattingcustoms']['threat_category_value'], 
            datetime.datetime.now(), username
        ]
        file_util.append_to_csv("threatData.csv", data_row)
        
        if trader_category.casefold() == 'customs_officer':
            return tno_chatbot.rule_enquiry(user_query)
        else:
            return 'We are unable to answer your query as it is not related to legal import and export for Singapore'