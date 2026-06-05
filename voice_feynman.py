import os
import subprocess
import speech_recognition as sr
from src.feynman_chain import build_feynman_chain


def text_to_speech_mac(text: str):
    if not text:
        return
    subprocess.run(["say", text], check=True)


os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")


def main():
    feynman = build_feynman_chain()

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Ask your question...")
        audio = r.listen(source)
        print("Recognizing...")
        question = r.recognize_google(audio)
        print("You said:", question)

    answer = feynman(question, long_term_memory_text="")
    print("Feynman:", answer)

    text_to_speech_mac(answer)


if __name__ == "__main__":
    main()