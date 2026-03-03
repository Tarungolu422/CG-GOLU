import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

def translate_text(text: str, source_language_code: str, target_language_code: str) -> str:
    """
    Translates text using Sarvam AI's translate API.
    Language codes: 'hi-IN' (Hindi), 'en-IN' (English), etc.
    If the API key is not present, returns the original text as a fallback.
    """
    if not SARVAM_API_KEY:
        print("Warning: SARVAM_API_KEY missing. Skipping translation.")
        return text
        
    url = "https://api.sarvam.ai/translate"
    
    payload = {
        "input": [text],
        "source_language_code": source_language_code,
        "target_language_code": target_language_code,
        "mode": "formal"
    }
    
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raise exception for bad status codes
        data = response.json()
        translated_text = data.get("translated_text", [])
        if translated_text:
            return translated_text[0] # The input is a list of 1 string
    except Exception as e:
        print(f"Error during Sarvam translation: {e}")
        
    return text

def translate_to_hindi(text: str, source_code: str = "en-IN") -> str:
    """Helper for converting input query to Hindi for better internal RAG matching."""
    return translate_text(text, source_code, "hi-IN")
    
def translate_to_english(text: str, source_code: str = "hi-IN") -> str:
    """Helper for converting output back to English if required."""
    return translate_text(text, source_code, "en-IN")

# Note: Sarvam currently supports Indic languages but may not have a dedicated 
# reliable API specifically for Chhattisgarhi just yet. We will configure 
# our LLM prompt to respond directly in Chhattisgarhi using the prompt template.
# This translation layer is primarily used for routing the USER query into Hindi/English for the Retrieval step.
