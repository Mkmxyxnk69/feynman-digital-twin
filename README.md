# Feynman Digital Twin

## Overview
This project is a digital twin of Richard Feynman that answers physics questions in his teaching style using RAG over curated notes, a long-term memory system, and a voice interface (speech-to-text + text-to-speech).

## Features
- Retrieval-augmented generation over Feynman-style notes (`data/` + `vectorstore/`)
- Long-term memory with summarized past interactions (`memory_store.py`, `memories.json`)
- Web UI with Streamlit (`app.py`) for chat, voice, and memory dashboard
- Voice Q&A using SpeechRecognition for STT and macOS `say` for TTS (`voice_feynman.py` and Voice tab)

## How to run

```bash
git clone https://github.com/Mkmxyxnk69/feynman-digital-twin.git
cd feynman-digital-twin
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

python -m streamlit run app.py
```

## Architecture (high level)
- User → Streamlit Chat/Voice UI (`app.py`)
- Feynman chain (`src/feynman_chain.py`) uses:
  - Persona prompt (`src/persona.py`)
  - RAG over Chroma vectorstore (`scripts/build_vectorstore.py`, `vectorstore/`)
  - Long-term memory context (`memory_store.py`, `memories.json`)
- Voice path:
  - Microphone → SpeechRecognition (Google STT) → Feynman chain
  - Answer text → macOS `say` → spoken reply

## Design decisions
- Chose Feynman persona for clear, intuitive explanations of physics
- Used RAG to keep responses grounded in specific Feynman-style notes
- Summarized memories instead of raw logs to keep context compact
- Implemented voice using Google STT + macOS `say` due to time and platform constraints

## Architecture

### High-level flow

User  
↓  
Streamlit UI (`app.py`)  
↓  
Feynman Chain (`src/feynman_chain.py`)  
↓  
RAG + Memory  
↓  
Answer (text + optional voice)

---

### Components and data flow

1. Chat flow (text)

User  
↓ (types question)  
**Streamlit UI – Chat tab (`app.py`)**  
- shows previous messages  
- takes `st.chat_input`  

↓ (sends `user_input` + `long_term_memory_text`)  

**Feynman Chain (`src/feynman_chain.py`)**  
- loads persona and config from `src/persona.py` and `src/config.py`  
- builds prompt with:
  - current question  
  - retrieved notes (RAG)  
  - recent memory summaries  

↓ (queries vectorstore)  

**RAG / Vectorstore**  
- built by `scripts/build_vectorstore.py`  
- uses `data/` Feynman notes  
- stored in `vectorstore/` (Chroma DB)  

↓ (returns top‑k relevant chunks)  

**Feynman Chain**  
- combines:
  - persona prompt  
  - user question  
  - RAG context  
  - memory context  
- calls LLM (Gemini)  
- produces Feynman-style answer  

↓  

**Streamlit UI – Chat tab**  
- displays answer  
- optional “🔊 Read this answer aloud” button (uses macOS `say`)  
- summarizes Q&A and sends to memory store  

↓  

**Memory System (`memory_store.py` + `memories.json`)**  
- stores:
  - question  
  - short answer summary  
  - timestamp  
- future questions load recent memories via `build_long_term_memory_text()`

---

2. Voice flow (speech → speech)

User  
↓ (speaks into microphone)  

**Voice Pipeline**  
- implemented in:
  - `voice_feynman.py` (terminal demo)  
  - Voice tab handler in `app.py`  
- uses:
  - `speech_recognition` + `PyAudio` for STT  
  - Google STT via `Recognizer().recognize_google()`  

↓ (produces text transcript)  

**Feynman Chain (same as Chat flow)**  
- uses RAG + memory exactly like text chat  

↓ (answer text)  

**Voice Pipeline**  
- calls `text_to_speech_mac()`  
- uses macOS `say` command to speak answer  

↓  

User hears spoken answer