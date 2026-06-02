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