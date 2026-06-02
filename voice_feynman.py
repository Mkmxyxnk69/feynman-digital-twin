import os
import subprocess
import speech_recognition as sr

from src.feynman_chain import build_feynman_chain


def text_to_speech_mac(text: str):
    if not text:
        return
    subprocess.run(["say", text], check=True)


# FLAC ke liye system path add karo (agar Homebrew flac yahan hai)
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")


def main():
    # Feynman chain banao (jaise tum app me karte ho)
    feynman = build_feynman_chain()

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Ask your question...")
        audio = r.listen(source)
        print("Recognizing...")
        question = r.recognize_google(audio)
        print("You said:", question)

    # Feynman se answer lo
    answer = feynman(question, long_term_memory_text="")
    print("Feynman:", answer)

    # Answer ko bolwao
    text_to_speech_mac(answer)


if __name__ == "__main__":
    main()