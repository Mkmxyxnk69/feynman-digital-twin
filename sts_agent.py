# sts_agent.py
import subprocess
from pathlib import Path

from src.feynman_chain import build_feynman_chain




def text_to_speech_mac(text: str) -> None:
    """
    Speak text aloud using macOS 'say' command.

    This uses the system TTS. It does not call any external API.
    """
    if not text:
        return

    subprocess.run(
        ["say", text],
        check=True
    )



def speech_to_text(audio_path: str) -> str:
    return "Explain the double-slit experiment in simple words."



def build_feynman_agent():
    """
    Build the Feynman chain once for this script.
    """
    feynman_chain = build_feynman_chain()
    return feynman_chain


def ask_feynman(feynman, question: str) -> str:
    """
    Ask the Feynman twin a question and return the answer text.
    """
    long_term_memory_text = ""
    answer = feynman(
        question,
        long_term_memory_text=long_term_memory_text,
    )
    return answer

def run_sts_once() -> None:
    """
    Run one full STS cycle with a dummy audio input:

    1. Use a placeholder STT output.
    2. Send text to Feynman twin.
    3. Speak the answer (TTS).
    """
    question = speech_to_text("dummy_path")
    print("[STS] Recognized question:", question)

    feynman = build_feynman_agent()
    answer = ask_feynman(feynman, question)
    print("[STS] Feynman answer:", answer)

    print("[STS] Speaking answer via macOS 'say' ...")
    text_to_speech_mac(answer)


if __name__ == "__main__":
    
    run_sts_once()