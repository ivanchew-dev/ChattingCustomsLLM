import glob
import os
from openai import OpenAI
from helper import key_util
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import logging

# Refer to LangChain documentation to find which loggers to set
# Different LangChain Classes/Modules have different loggers to set
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)


# This is the "Updated" helper function for calling LLM
ApiKey = key_util.return_open_api_key()
client = OpenAI(api_key=ApiKey)
# embedding model that we will use for the session
embeddings_model = OpenAIEmbeddings(model='text-embedding-3-small')
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
def get_embedding(input, model='text-embedding-3-small'):
    response = client.embeddings.create(
        input=input,
        model=model
    )
    return [x.embedding for x in response.data]

def textloader_for_files_in_directory(directory_path, file_mask):
    """
    Checks if a directory is valid and then processes files within it
    that match a given mask.

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

def rag_query(user_query:str):
    logging.basicConfig()
    logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
    # Load existing Chroma vector database
    vectordb = Chroma(
        collection_name='ecommerce_semantic', 
        persist_directory='./vector_db',
        embedding_function=embeddings_model
    )
    qa_chain_retrieval_process = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=vectordb.as_retriever()
                    )
    results = qa_chain_retrieval_process.invoke(user_query)
    if "don't know" in results['result']: 
        retriever_multiquery = MultiQueryRetriever.from_llm(
                    retriever=vectordb.as_retriever(), llm=llm
                )
        retriever = vectordb.as_retriever(search_type='mmr',
                                  search_kwargs={'k': 2, 'fetch_k': 3})
        qa_chain_multiquery_process = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=retriever_multiquery
                    )
        result=qa_chain_multiquery_process.invoke(user_query)
        return "Retrieval Multi : " + result['result']
    #print(embeddings_model)
    else:
        return "Retrieval QA : " + results['result']
    
def create_rag_prompt(message:str):
   prompt = ChatPromptTemplate.from_template(
    message
)
   return prompt
