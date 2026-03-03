import streamlit as st
import os
import time

# Enable LangSmith Tracing if API key is provided
if os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", os.getenv("LANGSMITH_API_KEY", ""))
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "CG_AI_Sahayak")

# We import the required backend logic
# In a real deployed app, you might want to lazily load heavy modules like embeddings
from src.components.llm_chain import ask_question
from src.components.multilingual import translate_to_hindi
from gtts import gTTS
from langdetect import detect
import requests
import base64
import re

def speak(text, lang_code):
    """Generates TTS audio using Sarvam API (with gTTS fallback) and returns (file_path, mime_type)."""
    sarvam_api_key = os.getenv("SARVAM_API_KEY")
    
    if sarvam_api_key:
        try:
            url = "https://api.sarvam.ai/text-to-speech"
            # Sarvam supports hi-IN for Hindi/Chhattisgarhi outputs beautifully
            target_lang = "hi-IN" if lang_code == "hi" else "en-IN"
            
            payload = {
                "inputs": [text[:500] if len(text)>500 else text], # limit payload length for TTS safety
                "target_language_code": target_lang,
                "speaker": "meera",
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.2,
                "speech_sample_rate": 8000,
                "enable_preprocessing": True,
                "model": "bulbul:v1"
            }
            
            headers = {
                "api-subscription-key": sarvam_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "audios" in data and len(data["audios"]) > 0:
                    audio_file = "response.wav"
                    with open(audio_file, "wb") as f:
                        f.write(base64.b64decode(data["audios"][0]))
                    return audio_file, "audio/wav"
            else:
                print(f"Sarvam TTS API Error: {response.text}")
        except Exception as e:
            print(f"Sarvam TTS failed: {e}. Falling back to gTTS.")
            
    # Fallback to gTTS if Sarvam is unavailable or fails
    audio_file = "response.mp3"
    tts = gTTS(text=text, lang=lang_code)
    tts.save(audio_file)
    return audio_file, "audio/mp3"

def transcribe_audio(audio_bytes):
    """Transcribes spoken audio into text using Sarvam AI Speech-to-Text."""
    sarvam_api_key = os.getenv("SARVAM_API_KEY")
    if not sarvam_api_key:
        st.error("SARVAM_API_KEY is missing for voice transcription.")
        return None
    try:
        url = "https://api.sarvam.ai/speech-to-text"
        files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
        data = {'language_code': 'hi-IN', 'model': 'saaras:v3'}
        headers = {"api-subscription-key": sarvam_api_key}
        response = requests.post(url, files=files, data=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("transcript", "")
        else:
            st.error(f"STT Error: {response.text}")
    except Exception as e:
        st.error(f"STT Exception: {e}")
    return None


# Page config
st.set_page_config(
    page_title="CG AI Sahayak 🌾",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #5D6D7E;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* Simple chat box styling override */
    .stChatMessage {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title Header
st.markdown('<div class="main-title">CG AI Sahayak 🌾</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">छत्तीसगढ़ शासन की योजनाएं अउ पर्यटन जानकारी (Govt Schemes & Tourism)</div>', unsafe_allow_html=True)

# Sidebar configurations
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check for API key
    if not os.getenv("SARVAM_API_KEY"):
        st.warning("⚠️ SARVAM_API_KEY is missing in .env. Responses might fail or default to open-source models if configured.")
        
    st.markdown("### Language Selection")
    language_mode = st.selectbox(
        "Response Language Mode",
        ["Chhattisgarhi (Default)", "Auto-Detect", "Hindi", "English"],
        index=0
    )
        
    st.markdown("### Search Filters (Coming Soon)")
    st.selectbox("Filter by District", ["All Chhattisgarh", "Bastar", "Raipur", "Surguja", "Bilaspur"])
    st.selectbox("Topic", ["Both", "Government Schemes", "Tourism"])
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "जय जोहार! मैं छत्तीसगढ़ एआई सहायक हंव। आप मन ल कइसन मदद चाही? (Hello! I am CG AI Sahayak. How can I help you today?)"}
        ]
        st.rerun()
        
    st.markdown("---")
    st.markdown("**Powered by:** LangChain, ChromaDB, Sarvam AI, gTTS")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "जय जोहार! मैं छत्तीसगढ़ एआई सहायक हंव। आप मन ल कइसन मदद चाही? (Hello! I am CG AI Sahayak. How can I help you today?)"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "audio" in msg:
            st.audio(msg["audio"], format=msg.get("mime_type", "audio/mp3"))

# User input
text_prompt = st.chat_input("Write your question here... (English, Hindi, or Chhattisgarhi)")
voice_prompt = st.audio_input("🎤 बोल के सवाल पूछव (Ask by speaking)")

prompt = text_prompt
if voice_prompt:
    with st.spinner("आवाज़ ल समझत हंव... (Transcribing...)"):
        transcription = transcribe_audio(voice_prompt)
        if transcription:
            prompt = transcription

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        audio_placeholder = st.empty()
        
        with st.spinner("विचार करत हंव... (Thinking...)"):
            try:
                # Determine language logic
                if language_mode == "Auto-Detect":
                    # Heuristics for Chhattisgarhi because langdetect treats it as Hindi
                    cg_markers = ["कइसे", "तभे", "ला", "मन", "मिलथे", "होथे", "आय", "हे", "हंव", "करहू", "जाही", "काबर", "बर", "अउ", "जाहूं", "का"]
                    prompt_words = prompt.split()
                    if any(marker in prompt_words for marker in cg_markers) or any(marker in prompt for marker in [" मिलथे ", " होथे ", " मन ", " हे"]):
                        final_language = "Chhattisgarhi"
                    else:
                        try:
                            detected_lang = detect(prompt)
                            if detected_lang == "hi":
                                final_language = "Hindi"
                            elif detected_lang == "en":
                                final_language = "English"
                            else:
                                final_language = "Chhattisgarhi"
                        except:
                            final_language = "Chhattisgarhi" # Fallback if detection fails
                else:
                    final_language = language_mode.replace(" (Default)", "")

                # Fetch Answer incorporating the language variable
                response = ask_question(prompt, language=final_language)
                
                # Setup TTS voice
                if final_language == "Hindi":
                    lang_code = "hi"
                elif final_language == "English":
                    lang_code = "en"
                else:
                    lang_code = "hi"  # Chhattisgarhi fallback via Hindi voice
                
                # Clean markdown characters (**, _, #) so the TTS doesn't read them aloud
                spoken_text = re.sub(r'[*_]{1,3}', '', response)
                spoken_text = re.sub(r'#+\s?', '', spoken_text)
                spoken_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', spoken_text)
                
                # Generate Audio
                audio_file, mime_type = speak(spoken_text, lang_code)
                
            except Exception as e:
                response = f"माफ़ करहू, तकनीकी त्रुटि आय हे: {str(e)}"
                audio_file = None
                mime_type = None
        
        # Display response
        message_placeholder.markdown(response)
        if audio_file:
            audio_placeholder.audio(audio_file, format=mime_type, autoplay=True)
            # Append audio to session state to persist playback capability
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "audio": audio_file,
                "mime_type": mime_type
            })
        else:
            st.session_state.messages.append({"role": "assistant", "content": response})
