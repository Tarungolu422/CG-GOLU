import os
from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms import OpenAI  # Fallback/standard LLM interface
from langchain_core.language_models.llms import LLM

# Due to Sarvam API being highly specialized, we can use their text-generation endpoint 
# via a custom LangChain wrapper, or just use OpenAI as a generic drop-in if a specific 
# wrapper isn't natively available in `langchain-community` yet. 
# For demonstration in this project, we'll wrap a basic HTTP call to their chat-completions endpoint if strictly Sarvam is required.
# Assuming they have an OpenAI-compatible endpoint route, we use ChatOpenAI.

from langchain_openai import ChatOpenAI

from src.components.vector_store import get_retriever
from src.prompts.system_prompt import get_rag_prompt

load_dotenv()

# We configure to use Sarvam AI API using an OpenAI compatible client configuration
# If they don't support it directly, you would implement a CustomLLM subclass.
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "dummy_key_for_testing")

def get_llm():
    """Initializes the LLM. Using ChatOpenAI class but pointing to Sarvam if possible, or defaulting to a given model."""
    # Assuming Sarvam provides an OpenAI-compatible endpoint like `https://api.sarvam.ai/v1`
    # If not, we fallback to a standard Langchain custom LLM approach.
    llm = ChatOpenAI(
        model="sarvam-m", # Valid Sarvam model name 
        api_key=SARVAM_API_KEY,   
        base_url="https://api.sarvam.ai/v1", # Replace with actual Sarvam completions endpoint
        temperature=0.1, # Keep it low to prevent hallucination
        max_tokens=500
    )
    return llm

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def setup_rag_chain():
    """Builds and returns the LCEL (LangChain Expression Language) Retrieval chain."""
    retriever = get_retriever(k=5)
    llm = get_llm()
    prompt = get_rag_prompt()
    
    rag_chain = (
        {
            "context": lambda x: format_docs(retriever.invoke(x["question"])),
            "question": lambda x: x["question"],
            "language": lambda x: x["language"]
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

# Master-Level Dialect Translation Filter List (Based on Deep Chhattisgarhi Linguistic Rules)
CG_REPLACEMENTS = {
    "एह ": "ए ",
    "एतय": "इहाँ",
    "ओतय": "ओतका",
    "काहाँ": "कइँहा",
    "तोहर": "तोर",
    "हमनी": "हमन",
    "रउआ": "तें",
    "जाइत": "जाथे",
    "अछि": "हे",
    "गेल": "गे",
    " में ": " म ",
    " को ": " ला ",
    " और ": " अऊ ",
    " नहीं ": " नइ ",
    "लोग ": " मन ",
    "बनवाओल": "बनाय",
    "होइत": "होथे",
    "कहल": "कहे",
    "आवत": "आथे",
    "जिल्ला": "जिला",
    " लेल ": " बर ",
    "एकटा": "एक",
    "राजे मंनि": "राजा मन",
    "बनायल": "बनाय",
    "जतय": "जिहाँ",
    "के आराधना": "ला समर्पित",
    
    # Advanced AI Master-Level Injections
    "मेरा ": "मोर ",
    "तुम्हारा ": "तोर ",
    "उसका ": "ओकर ",
    "हमारा ": "हमर ",
    "किधर": "कति",
    "इधर": "एति",
    "उधर": "ओति",
    "यहाँ": "इहाँ",
    "वहाँ": "उहाँ",
    " बहुत ": " अब्बड़ ",
    " थोड़ा ": " थोरिक ",
    "सुबह": "बिहनिया",
    "शाम": "संझा",
    "दोपहर": "मंझनिया",
    "कल ": "काली ",
    "आदमी": "मनखे",
    "लड़का": "लइका",
    "लड़की": "नोनी",
    "कर रहा है": "करत हे",
    "जा रहा है": "जावत हे",
    "आ रहा है": "आवत हे",
    "खा रहा है": "खावत हे",
    "करेगा": "करही",
    "जाएगा": "जाही",
    "आएगा": "आही",
    "खाएगा": "खाही",
    "रुकना": "रुकना",
    "देखना": "देखना",
    " जानना ": " जानना "
}

def correct_dialect(text: str) -> str:
    """Post-processing filter to enforce pure Chhattisgarhi and remove Bhojpuri/Maithili bleed."""
    for wrong, correct in CG_REPLACEMENTS.items():
        text = text.replace(wrong, correct)
    return text

def ask_question(question: str, language: str = "Chhattisgarhi") -> str:
    """Entry point to ask a question to the system."""
    chain = setup_rag_chain()
    try:
        response = chain.invoke({"question": question, "language": language})
        # Apply Zero-Latency Dialect Polishing Layer
        if language == "Chhattisgarhi":
            response = correct_dialect(response)
        return response
    except Exception as e:
        return f"माफ़ करहू, कुच्छु तकनीकी समस्या आ गे हे: {str(e)}" # Sorry, there is some technical issue
        
if __name__ == "__main__":
    # Test
    print(ask_question("What are the benefits of the Rajiv Gandhi Kisan Nyay Yojana?"))
