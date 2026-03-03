import json
import os
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_json_data(file_path: str) -> List[dict]:
    """Load data from a JSON file."""
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found.")
        return []
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def process_schemes(data: List[dict]) -> List[Document]:
    """Convert scheme JSON objects into Langchain Documents."""
    docs = []
    for item in data:
        # Create a rich text representation of the scheme
        content = f"Scheme Name: {item.get('scheme_name', 'N/A')}\n"
        content += f"Department: {item.get('department', 'N/A')}\n"
        content += f"Eligibility: {item.get('eligibility', 'N/A')}\n"
        content += f"Benefits: {item.get('benefits', 'N/A')}\n"
        
        req_docs = item.get('documents_required', [])
        if req_docs:
            content += f"Documents Required: {', '.join(req_docs)}\n"
            
        content += f"Official Link: {item.get('official_link', 'N/A')}"
        
        metadata = {
            "source": "schemes",
            "name": item.get('scheme_name', 'Unknown')
        }
        
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

def process_tourism(data: List[dict]) -> List[Document]:
    """Convert tourism JSON objects into Langchain Documents."""
    docs = []
    for item in data:
        # Create a rich text representation of the tourism place
        content = f"Place Name: {item.get('place_name', 'N/A')}\n"
        content += f"District: {item.get('district', 'N/A')}\n"
        content += f"Category: {item.get('category', 'N/A')}\n"
        content += f"Description: {item.get('description', 'N/A')}\n"
        content += f"Best Time to Visit: {item.get('best_time_to_visit', 'N/A')}"
        
        metadata = {
            "source": "tourism",
            "name": item.get('place_name', 'Unknown'),
            "district": item.get('district', 'Unknown')
        }
        
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

def get_chunked_documents(data_dir: str = "./data", chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Document]:
    """
    Reads JSON files, parses them, and chunks the texts into Document objects.
    """
    all_raw_docs = []
    
    # 1. Process Schemes
    schemes_path = os.path.join(data_dir, "schemes.json")
    schemes_data = load_json_data(schemes_path)
    all_raw_docs.extend(process_schemes(schemes_data))
    
    # 2. Process Tourism
    tourism_path = os.path.join(data_dir, "tourism.json")
    tourism_data = load_json_data(tourism_path)
    all_raw_docs.extend(process_tourism(tourism_data))
    
    # 3. Text Splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunked_docs = text_splitter.split_documents(all_raw_docs)
    return chunked_docs

if __name__ == "__main__":
    # Test the ingestion independently
    docs = get_chunked_documents("../../data")
    print(f"Total chunks created: {len(docs)}")
    if docs:
        print("\nSample Target Doc:")
        print(docs[0].page_content)
        print("Metadata:", docs[0].metadata)
