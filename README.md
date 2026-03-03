# CG AI Sahayak – Chhattisgarh Government Schemes & Tourism Multilingual Chatbot

## Overview
A powerful, multilingual chatbot built using Retrieval-Augmented Generation (RAG) to provide up-to-date information on Chhattisgarh Government Schemes and Tourism. It understands English, Hindi, and Chhattisgarhi, and replies specifically in Chhattisgarhi by default.

## Features
- **Multilingual Support**: Input queries in English, Hindi, or Chhattisgarhi. Responses are translated and delivered in Chhattisgarhi.
- **RAG Pipeline**: Retrieves facts directly from verified data sources to eliminate hallucination.
- **Government & Tourism Focus**: Contains data on schemes (eligibility, benefits) and tourist hotspots.
- **Context-Aware LLM**: Powered by Sarvam AI to maintain cultural nuances and respectful tones.
- **Streamlit Interface**: Clean, accessible, and user-friendly interaction.

## Folder Structure
```text
project_root/
│
├── data/
│   ├── schemes.json          # Raw data for schemes
│   └── tourism.json          # Raw data for tourism places
│
├── src/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── data_ingestion.py # Loads JSON and chunks data
│   │   ├── vector_store.py   # ChromaDB integration and embeddings
│   │   ├── multilingual.py   # Sarvam API translation functions
│   │   └── llm_chain.py      # LangChain Retrieval QA Chain assembly
│   └── prompts/
│       ├── __init__.py
│       └── system_prompt.py  # Prompt logic to enforce output behavior
│
├── app.py                    # Streamlit app frontend
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Setup Instructions
1. Clone the repository and navigate to the folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your Sarvam AI API keys.
4. Run the data ingestion script (optional run locally first) or let the app ingest on startup.
5. Run the Streamlit application: `streamlit run app.py`

## Future Scope (Government-Grade System)
- Role-based access control (RBAC).
- Administrator Dashboard & Analytics.
- Logging & Monitoring using standard tools (ELK stack / Datadog).
- Agentic eligibility checker for real-time validation via external APIs.
