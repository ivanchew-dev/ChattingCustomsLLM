from helper import prompt_util
from helper import rag_util

extraction_list = """
XML Tag Mapping for Trade Declaration Fields:
- <submissiondate> = Date Of Submission
- <dateofdeparture> = Date Of Departure  
- <place> = Place
- <address> = Address
- <changeindicator> = Change Indicator
- <carts> = Cart Information
- <cartnumberinformation> = Cart Number Information
- <sequencenumber> = Sequence Number
- <userid> = User ID
- <type> = Transaction Type
- <actioncode> = Action Code
- <mailboxid> = Mailbox ID
"""
def declaration_xml_enquiry(user_query:str):
    system_message = f"""XML validator to ensure the xml is well formed and valid."""
    messages =  [
    {'role':'system',
    'content': system_message},
    {'role':'user',
    'content': f"<incoming-message>{user_query}</incoming-message>"},
    ]

    return prompt_util.get_completion_from_messages(messages)
def is_user_query_xml(user_query:str):
    system_message = f"""
Determine if the user query contains XML-like tags for trade declaration data.

**Instructions:**
- Look for XML tags like <tagname>value</tagname>
- Check if the query contains structured trade declaration data
- Return exactly "true" if XML-like structure is detected
- Return exactly "false" if it's a regular text question

**Examples of XML queries:**
- <dateofdeparture>20251023</dateofdeparture><place>A</place>
- <userid>buy123</userid><type>PURCHASE</type>

**Examples of non-XML queries:**
- "How do I import goods to Singapore?"
- "What are the customs procedures?"

Return only "true" or "false" - no other text.

The user query will be enclosed in <incoming-message></incoming-message> tags.
"""
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"<incoming-message>{user_query}</incoming-message>"}
    ]

    return prompt_util.get_completion_from_messages(messages)
def extract_user_query_xml(user_query:str):
    system_message = f"""
Extract XML fields from the user query and return them as a readable summary.

**Extraction Mapping:**
{extraction_list}

**Instructions:**
- Find XML tags in the user query that match the extraction list
- If a tag is present, extract its value
- If a tag is missing or empty, note it as "not provided"
- Return a clear text summary of all extracted fields

**Format your response as:**
Field Name: [extracted value or "not provided"]

The user query will be enclosed in <incoming-message></incoming-message> tags.
"""
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"<incoming-message>{user_query}</incoming-message>"}
    ]

    return prompt_util.get_completion_from_messages(messages)
def rule_enquiry(user_query:str):
    is_query_xml = is_user_query_xml(user_query)
    print("user query " + user_query.upper())
    
    # Initialize variables
    xmlFieldsValue = ""
    
    if (is_query_xml.casefold() == "true"):
        xmlFieldsValue = extract_user_query_xml(user_query.upper())
        print ("xmlFieldsValue: " + xmlFieldsValue)
        rag_query_text = "Retrieve the rules related to " + xmlFieldsValue
    else:
        rag_query_text = "Retrieve the general trading rules for " + user_query
    
    rag_response = rag_util.rag_query(rag_query_text)
    print(rag_response)
    
    if (is_query_xml.casefold() == "true"):
        system_message = f"""
You are a Singapore Customs officer with expertise in trade regulations and technical jargon.

**Your Task:**
1. Extract XML data from the user query based on: {extraction_list}
2. Apply the RAG context rules to validate compliance
3. Provide a clear, step-by-step markdown response

**RAG Context (Rules Database):**
{rag_response}

**Instructions:**
- Use ONLY the provided RAG context for validation rules
- If XML tags are missing, treat their values as empty/not filled
- Structure your response with clear headings and bullet points
- Use ✅ for PASS/ALLOW and ❌ for FAIL/REJECT outcomes
- Provide detailed explanations for each validation step
- End with a clear **Final Outcome** section

**Response Format:**
```markdown
# Trade Declaration Validation Report

## 📋 Extracted Data
[List all extracted XML fields and their values]

## 🔍 Rule Validation Steps
[Step-by-step validation against each applicable rule]

## 📊 Final Outcome
**Status:** ✅ APPROVED / ❌ REJECTED
**Reason:** [Clear explanation]
```

The user query will be enclosed in <incoming-message></incoming-message> tags.
"""
    else:
        system_message = f"""
You are a Singapore Customs officer providing guidance on trade regulations.

**RAG Context (Knowledge Base):**
{rag_response}

**Instructions:**
- Use ONLY the provided RAG context to answer the query
- Structure your response in clear markdown format
- Provide step-by-step explanations
- Use bullet points and headings for readability
- Include relevant regulatory references when available
- If the RAG context doesn't contain relevant information, state "no-idea" clearly

**Response Format:**
```markdown
# Singapore Customs Guidance

## 📝 Query Analysis
[Brief summary of the question]

## 📋 Step-by-Step Response
[Detailed guidance based on RAG context]

## 🔗 Additional Information
[Any relevant regulatory notes or references]

## 📊 Final Recommendation
**Conclusion:** [Clear actionable guidance]
```

The user query will be enclosed in <incoming-message></incoming-message> tags.
"""
    
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"<incoming-message>{user_query.upper()}</incoming-message>"}
    ]
    
    return prompt_util.get_completion_from_messages(messages)