# Feynman Digital Twin

## Overview
This project is a digital twin of Richard Feynman that answers physics questions in his teaching style using retrieval‑augmented generation (RAG) over curated notes, a simple long‑term memory system, and an optional voice interface (speech‑to‑text + text‑to‑speech).

## Features
- Retrieval‑augmented generation over Feynman‑style physics notes in `data/` backed by a Chroma vectorstore in `vectorstore/`.
- Long‑term memory with summarized past interactions stored in `memories.json` and managed via `memory_store.py`.
- Web UI built with Streamlit (`app.py`) for chat, basic voice control, and a simple memory view.
- Voice Q&A demo using SpeechRecognition for STT and macOS `say` for TTS (`voice_feynman.py`).
- Separate test scripts for quickly checking the LLM and the Feynman chain (`src/test_gemini.py`, `src/test_feynman_chain.py`).

## How to run

```bash
git clone https://github.com/Mkmxyxnk69/feynman-digital-twin.git
cd feynman-digital-twin

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Set your Gemini API key in `.env`:

```bash
GEMINI_API_KEY=your_key_here
```

Then run the Streamlit app:

```bash
python -m streamlit run app.py
```

Optional quick tests:

```bash
python -m src.test_gemini          # check LLM connectivity
python -m src.test_feynman_chain   # check RAG + Feynman chain end-to-end
python voice_feynman.py            # terminal voice demo (macOS)
```

## Architecture (high level)
- User → Streamlit Chat/Voice UI (`app.py`)
- Feynman chain (`src/feynman_chain.py`) uses:
  - Persona prompt (`src/persona.py`)
  - Config (`src/config.py`) for model, vectorstore path, and retrieval parameters
  - RAG over Chroma vectorstore (`scripts/build_vectorstore.py`, `vectorstore/`)
  - Long‑term memory context (`memory_store.py`, `memories.json`)
- Voice path:
  - Microphone → SpeechRecognition (Google STT) → Feynman chain
  - Answer text → macOS `say` → spoken reply

## Design decisions
- Chose a Feynman persona to emphasize intuitive, step‑by‑step physics explanations.
- Used a simple RAG pipeline (top‑k retrieval from Chroma) to keep answers grounded in the curated notes instead of hallucinating.
- Represented long‑term memory as short summaries of past Q&A, which keeps context compact but still lets the agent “remember” earlier conversations.
- Implemented voice using Google STT and the macOS `say` command to avoid heavy dependencies and keep the demo easy to run on a single laptop.
- Kept the chain logic in `src/feynman_chain.py` small and testable so it can be reused from both the Streamlit app and the standalone scripts.

## Architecture details

### High‑level flow

User  
↓  
Streamlit UI (`app.py`)  
↓  
Feynman chain (`src/feynman_chain.py`)  
↓  
RAG + memory context  
↓  
Answer (text, optional voice)

---

### Components and data flow

#### 1. Chat flow (text)

User  
↓ (types question)  

**Streamlit UI – Chat tab (`app.py`)**  
- Shows previous messages  
- Collects `user_input`  
- Loads recent memory summaries  

↓  

**Feynman Chain (`src/feynman_chain.py`)**  
- Loads persona from `src/persona.py` and config from `src/config.py`  
- Calls a retriever over the Chroma vectorstore for top‑k relevant chunks  
- Builds a prompt with:
  - Current question  
  - Retrieved note chunks  
  - Long‑term memory text  

↓  

**RAG / Vectorstore**  
- Built once by `scripts/build_vectorstore.py` from text files in `data/`  
- Stored in `vectorstore/` as a Chroma DB  

↓  

**Feynman Chain**  
- Combines persona prompt + question + RAG context + memory context  
- Calls Gemini via the configured chat model  
- Returns a Feynman‑style answer  

↓  

**Streamlit UI – Chat tab**  
- Displays the answer  
- Optional button to read the answer aloud (using macOS `say`)  
- Summarizes the interaction and sends it to the memory store  

↓  

**Memory System (`memory_store.py` + `memories.json`)**  
- Appends:
  - User question  
  - Short summary of the answer  
  - Timestamp  
- Future questions include a slice of these summaries in the context.

---

#### 2. Voice flow (speech → speech)

User  
↓ (speaks into microphone)  

**Voice pipeline**  
- Implemented in:
  - `voice_feynman.py` (terminal demo)  
  - Voice tab handler in `app.py`  
- Uses:
  - `speech_recognition` + `PyAudio` for speech‑to‑text  
  - Google STT via `Recognizer().recognize_google()`  

↓ (text transcript)  

**Feynman Chain**  
- Same logic as text chat (RAG + memory + persona)  

↓ (answer text)  

**Voice pipeline**  
- Passes answer text to `text_to_speech_mac()`  
- Uses the `say` command to speak the response aloud  

↓  

User hears spoken answer