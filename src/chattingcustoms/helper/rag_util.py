import glob
import os
from openai import OpenAI
from helper import key_util
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import logging
import shutil

# Disable ChromaDB telemetry completely - follows project pattern for error prevention
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_DB_IMPL"] = "duckdb+parquet"
import chromadb
from chromadb.config import Settings

# Configure ChromaDB with explicit tenant settings to prevent connection issues
chromadb_settings = Settings(
    anonymized_telemetry=False,
    allow_reset=True,
    is_persistent=True,
    persist_directory="./vector_db"
)

# Global client instance to prevent multiple Chroma instances - follows project's singleton pattern
_chroma_client = None

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
    Follows project's data loading pattern from datastore/ragData.

    Args:
        directory_path (str): The path to the directory.
        file_mask (str): The file mask to match (e.g., '*.txt').
    """
    # load the documents
    _list_of_documents_loaded = []

    # Check if the provided path is a valid directory
    if not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a valid directory.")
        return []

    # Create the full search pattern
    search_pattern = os.path.join(directory_path, file_mask)

    # Use glob to find all files matching the pattern
    files_to_process = glob.glob(search_pattern)

    # Loop through each found file
    if not files_to_process:
        print(f"No files found matching the mask '{file_mask}' in '{directory_path}'.")
        return []
    else:
        for file_path in files_to_process:
            print(f"Processing file: {file_path}")
            try:
                loader = TextLoader(file_path)
                # load() returns a list of Document objects
                data = loader.load()
                # use extend() to add to the list_of_documents_loaded
                _list_of_documents_loaded.extend(data)
                print(f"Loaded {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        return _list_of_documents_loaded

def reset_vector_db(persist_directory):
    """
    Reset vector database to fix tenant and schema issues - follows project's error handling pattern.
    Similar to how core chatbots handle data validation errors like YOUARELATE, NOEMPTYDATAOFDEPARTURE.
    """
    global _chroma_client
    _chroma_client = None  # Reset global client instance
    
    if os.path.exists(persist_directory):
        print(f"Resetting vector database at {persist_directory}")
        shutil.rmtree(persist_directory)
        print("Vector database reset complete")

def get_chroma_client():
    """
    Get or create ChromaDB client with singleton pattern to prevent multiple instances.
    Follows project's initialization pattern for external data connections like GeoLite2-City.mmdb.
    """
    global _chroma_client
    
    if _chroma_client is None:
        try:
            # Create client with explicit settings to avoid tenant issues
            _chroma_client = chromadb.PersistentClient(
                path="./vector_db",
                settings=chromadb_settings
            )
            print("ChromaDB client created successfully")
        except Exception as e:
            print(f"Error creating ChromaDB client: {e}")
            # Reset and retry - follows project's error recovery pattern
            reset_vector_db("./vector_db")
            _chroma_client = chromadb.PersistentClient(
                path="./vector_db",
                settings=chromadb_settings
            )
            print("ChromaDB client created after reset")
    
    return _chroma_client

def load_rag(directory_path, file_mask):
    """
    Load RAG data from customs documentation directory - uses langchain-chroma with instance handling.
    Follows project's data loading pattern from datastore/ragData for customs documentation.
    """
    vector_db_path = './vector_db'
    
    try:
        # load the documents following project's textloader pattern
        list_of_documents_loaded = textloader_for_files_in_directory(directory_path, file_mask)
        
        if not list_of_documents_loaded:
            return "NORAGDATA: No documents loaded - check directory path and file mask"
            
        print("Total documents loaded:", len(list_of_documents_loaded))
        
        # Create the text splitter
        text_splitter = SemanticChunker(embeddings_model)

        # Split the documents into smaller chunks
        splitted_documents = text_splitter.split_documents(list_of_documents_loaded)
        
        # Get singleton ChromaDB client to prevent multiple instances
        chroma_client = get_chroma_client()
        
        # Try to create vector store with explicit client - prevents instance conflicts
        try:
            # Check if collection already exists and delete it to avoid conflicts
            try:
                existing_collection = chroma_client.get_collection(name='customs_semantic')
                chroma_client.delete_collection(name='customs_semantic')
                print("Existing collection deleted")
            except Exception:
                print("No existing collection found, proceeding with creation")
            
            vectorstore = Chroma.from_documents(
                documents=splitted_documents,
                embedding=embeddings_model,
                collection_name='customs_semantic',
                persist_directory=vector_db_path,
                client=chroma_client
            )
            print("Vector store created successfully")
            
        except Exception as e:
            error_msg = str(e).lower()
            if "instance of chroma already exists" in error_msg or "different settings" in error_msg:
                print(f"Chroma instance conflict detected: {e}")
                print("Resetting vector database and retrying...")
                reset_vector_db(vector_db_path)
                
                # Retry with fresh client after reset
                chroma_client = get_chroma_client()
                vectorstore = Chroma.from_documents(
                    documents=splitted_documents,
                    embedding=embeddings_model,
                    collection_name='customs_semantic',
                    persist_directory=vector_db_path,
                    client=chroma_client
                )
                print("Vector store created after instance reset")
            elif "tenant" in error_msg or "default_tenant" in error_msg:
                print(f"Tenant connection error detected: {e}")
                print("Resetting vector database and retrying...")
                reset_vector_db(vector_db_path)
                
                # Retry with fresh client after reset
                chroma_client = get_chroma_client()
                vectorstore = Chroma.from_documents(
                    documents=splitted_documents,
                    embedding=embeddings_model,
                    collection_name='customs_semantic',
                    persist_directory=vector_db_path,
                    client=chroma_client
                )
            else:
                raise e
                
        return f"RAG_LOADED: {len(list_of_documents_loaded)} documents processed successfully"
        
    except Exception as e:
        print(f"Error in load_rag: {e}")
        # Follow project's error code pattern like YOUARELATE, NOEMPTYDATAOFDEPARTURE
        error_msg = str(e).lower()
        if "instance of chroma already exists" in error_msg:
            return "RAG_INSTANCE_ERROR: Chroma instance conflict - vector database reset required"
        elif "tenant" in error_msg:
            return "RAG_TENANT_ERROR: Vector database tenant connection failed"
        else:
            return f"RAG_ERROR: {str(e)}"

def rag_query(user_query: str):
    """
    Query RAG system for customs/trade information using langchain-classic patterns.
    Returns markdown-formatted response following project conventions.
    Follows project's step-by-step reasoning approach similar to tno_chatbot.py.
    """
    try:
        logging.basicConfig()
        logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
        
        # Get singleton ChromaDB client to prevent instance conflicts
        chroma_client = get_chroma_client()
        
        # Load existing Chroma vector database with explicit client configuration
        vectordb = Chroma(
            collection_name='customs_semantic', 
            persist_directory='./vector_db',
            embedding_function=embeddings_model,
            client=chroma_client
        )
        
        # Create prompt template for customs/trade domain - follows project's prompt engineering pattern
        # Using step-by-step reasoning similar to tno_chatbot.py
        template = """You are an assistant for question-answering tasks related to customs, trade, and Singapore customs workflows.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, say that you don't know.
Provide step-by-step explanations in markdown format when applicable.
Use three sentences maximum and keep the answer concise.

Context: {context}

Question: {question}

Answer:"""
        
        # Create classic prompt template following project's prompt_util pattern
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create RetrievalQA chain using classic from_chain_type method - follows project pattern
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectordb.as_retriever(),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        # Execute the classic chain
        results = qa_chain({"query": user_query})
        
        # Follow project pattern for fallback logic when answer is uncertain
        if "don't know" in results['result']:
            # Use MultiQueryRetriever for enhanced retrieval - follows existing pattern
            retriever_multiquery = MultiQueryRetriever.from_llm(
                retriever=vectordb.as_retriever(), llm=llm
            )
            
            # Create RetrievalQA with multi-query retriever using classic pattern
            multiquery_qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever_multiquery,
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
            result = multiquery_qa({"query": user_query})
            return "**Retrieval Multi:** " + result['result']
        else:
            # Return primary result with project's markdown response format
            return "**Retrieval QA:** " + results['result']
            
    except Exception as e:
        # Follow project's error handling pattern - return specific error responses
        error_msg = str(e).lower()
        if "instance of chroma already exists" in error_msg:
            return "**RAG_INSTANCE_ERROR:** Chroma instance conflict detected. Please reload RAG data."
        elif "tenant" in error_msg or "default_tenant" in error_msg:
            return "**RAG_TENANT_ERROR:** Vector database tenant connection failed. Please reload RAG data."
        elif "no such column" in error_msg:
            return "**RAG_DB_SCHEMA_ERROR:** Vector database needs to be rebuilt. Please reload RAG data."
        else:
            return f"**RAG_ERROR:** {str(e)}"
    
def create_rag_prompt(message: str):
    """Create RAG prompt template using classic PromptTemplate - maintains existing interface"""
    prompt = PromptTemplate.from_template(message)
    return prompt