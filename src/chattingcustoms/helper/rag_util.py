import glob
import os
from openai import OpenAI
from helper import key_util
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import logging

# Refer to LangChain documentation to find which loggers to set
# Different LangChain Classes/Modules have different loggers to set
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

# This is the "Updated" helper function for calling LLM - follows project pattern
ApiKey = key_util.return_open_api_key()
client = OpenAI(api_key=ApiKey)
# embedding model that we will use for the session
embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small')
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

def get_embedding(input, model='text-embedding-3-small'):
    """Get embeddings using OpenAI API - maintains existing interface"""
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]

def textloader_for_files_in_directory(directory_path, file_mask):
    """
    Checks if a directory is valid and then processes files within it
    that match a given mask - used for loading customs documentation.

    Args:
        directory_path (str): The path to the directory.
        file_mask (str): The file mask to match (e.g., '*.txt').
    """
    # load the documents
    _list_of_documents_loaded = []

    # Check if the provided path is a valid directory
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a valid directory.")
        return

    # Create the full search pattern
    search_pattern = os.path.join(directory_path, file_mask)

    # Use glob to find all files matching the pattern
    files_to_process = glob.glob(search_pattern)

    # Loop through each found file
    if not files_to_process:
        print(f"No files found matching the mask '{file_mask}' in '{directory_path}'.")
    else:
        for file_path in files_to_process:
            print(f"Processing file: {file_path}")
            loader = TextLoader(file_path)

            # load() returns a list of Document objects
            data = loader.load()
            # use extend() to add to the list_of_documents_loaded
            _list_of_documents_loaded.extend(data)
            print(f"Loaded {file_path}")
        return _list_of_documents_loaded

def load_rag(directory_path, file_mask):
    """Load RAG data from customs documentation directory"""
    # load the documents
    list_of_documents_loaded = []
    list_of_documents_loaded = textloader_for_files_in_directory(directory_path, file_mask)
    print("Total documents loaded:", len(list_of_documents_loaded))
    # Create the text splitter
    text_splitter = SemanticChunker(embeddings_model)

    # Split the documents into smaller chunks
    splitted_documents = text_splitter.split_documents(list_of_documents_loaded)
    Chroma.from_documents(splitted_documents, embeddings_model, collection_name='ecommerce_semantic', persist_directory='./vector_db')
    return "Total documents loaded:", len(list_of_documents_loaded)

def rag_query(user_query: str):
    """
    Query RAG system for customs/trade information using latest LangChain patterns.
    Returns markdown-formatted response following project conventions.
    """
    logging.basicConfig()
    logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
    
    # Load existing Chroma vector database
    vectordb = Chroma(
        collection_name='ecommerce_semantic', 
        persist_directory='./vector_db',
        embedding_function=embeddings_model
    )
    
    # Create system prompt for customs/trade domain - follows project's prompt engineering pattern
    system_prompt = (
        "You are an assistant for question-answering tasks related to customs, trade, and Singapore customs workflows. "
        "Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, say that you don't know. "
        "Provide step-by-step explanations in markdown format when applicable. "
        "Use three sentences maximum and keep the answer concise."
        "\n\n"
        "{context}"
    )
    
    # Create prompt template following project's ChatPromptTemplate pattern
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Create the document chain using latest LangChain methods
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    
    # Create the retrieval chain
    retrieval_chain = create_retrieval_chain(vectordb.as_retriever(), question_answer_chain)
    
    # Execute the chain
    results = retrieval_chain.invoke({"input": user_query})
    
    # Follow project pattern for fallback logic when answer is uncertain
    if "don't know" in results['answer']: 
        # Use MultiQueryRetriever for enhanced retrieval - follows existing pattern
        retriever_multiquery = MultiQueryRetriever.from_llm(
            retriever=vectordb.as_retriever(), llm=llm
        )
        
        # Create retrieval chain with multi-query retriever
        multiquery_chain = create_retrieval_chain(retriever_multiquery, question_answer_chain)
        result = multiquery_chain.invoke({"input": user_query})
        return "Retrieval Multi : " + result['answer']
    else:
        # Return primary result with project's response format
        return "Retrieval QA : " + results['answer']
    
def create_rag_prompt(message: str):
    """Create RAG prompt template - maintains existing interface"""
    prompt = ChatPromptTemplate.from_template(message)
    return prompt