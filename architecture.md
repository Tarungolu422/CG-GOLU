# CG AI Sahayak Architecture

## High-Level Flow
1. **User Input:** The user asks a question via Streamlit UI in English, Hindi, or Chhattisgarhi.
2. **Language Handling:**
   - Input language is detected.
   - If the input is in English or Chhattisgarhi, it is internally translated to Hindi using the Sarvam API for better vector representation and search quality (since most source data might be in Hindi/English, and LLMs reason well in Hindi compared to regional dialects). Alternatively, we keep it in English/Hindi depending on the data. For this pipeline, we will use English/Hindi embeddings.
3. **Retrieval (RAG):**
   - The query is embedded using `sentence-transformers`.
   - We search the `ChromaDB` vector database containing chunked JSON data of Government Schemes and Tourism sites.
   - Top-K relevant chunks are retrieved.
4. **LLM Generation:**
   - A prompt is constructed containing the retrieved context and the user's query.
   - The prompt enforces strict adherence to context (no hallucination) and instructs the model to generate the final response **specifically in Chhattisgarhi** (with a polite tone).
   - Sarvam AI API (or another compatible LLM endpoint) generates the response.
5. **Output Presentation:** The Streamlit interface displays the Chhattisgarhi response to the user.

## Vector Store Strategy
- **Documents:** `schemes.json` and `tourism.json` are loaded and converted into LangChain Document objects.
- **Chunking:** `RecursiveCharacterTextSplitter` is used to create manageable chunks.
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` or Sarvam embeddings.
- **Database:** `ChromaDB` persisted locally in `./chroma_db`.

## System Expansion (Government-grade plan)
- **Role-based Access:** To differentiate between general users and department admins who update the knowledge base.
- **Analytics Dashboard:** To track usage, frequent questions, and fallback queries.
- **Agentic Eligibility Checker:** A structured tool allowing the LLM to ask follow-up questions to determine if a user specifically qualifies for a scheme, rather than just reciting rules.
