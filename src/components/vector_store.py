import os
from typing import List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from src.components.data_ingestion import get_chunked_documents

# Directory to persist the Chroma database
CHROMA_PERSIST_DIR = "./chroma_db"

def get_embeddings() -> HuggingFaceEmbeddings:
    """Initialize the embedding model. Using an open-source lightweight model for fast local runs."""
    # Upgraded to a multilingual embedding space so Hindi/Chhattisgarhi queries 
    # successfully soft-match the English place names and district tags in the JSON.
    return HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def setup_vector_store() -> Chroma:
    """
    Initializes or loads the Chroma vector store.
    If the store doesn't exist or is empty, it ingests data from the data folder.
    """
    embeddings = get_embeddings()
    
    # Check if we should initialize and ingest data
    if not os.path.exists(CHROMA_PERSIST_DIR) or not os.listdir(CHROMA_PERSIST_DIR):
        print("Initializing new vector store from data...")
        docs = get_chunked_documents(data_dir="./data")
        
        if not docs:
            print("Warning: No documents found to ingest. Creating empty vector store.")
            
        vector_store = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )
        print(f"Successfully ingrained {len(docs)} document chunks.")
    else:
        print("Loading existing vector store...")
        vector_store = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embeddings
        )
        
    return vector_store

def get_retriever(search_type: str = "similarity", search_kwargs: dict = None, k: int = 5):
    """Returns a retriever interface for the vector store."""
    vector_store = setup_vector_store()
    if search_kwargs is None:
        search_kwargs = {"k": k}
    return vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

if __name__ == "__main__":
    # Test retrieving
    retriever = get_retriever()
    results = retriever.invoke("waterfall")
    print(f"Found {len(results)} results for 'waterfall'")
    for res in results:
        print(res.page_content)
