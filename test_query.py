import os
from dotenv import load_dotenv

load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", os.getenv("LANGSMITH_API_KEY", ""))

from src.components.llm_chain import ask_question

print("\n--- Testing RAG Answer Generation ---")
question = "tell me tourist place in Bilaspur"
print(f"Question: {question}")
print("Generating Answer (this may take a few seconds)...\n")
try:
    response = ask_question(question, language="Chhattisgarhi")
    print(response)
except Exception as e:
    print(f"Failed: {e}")
