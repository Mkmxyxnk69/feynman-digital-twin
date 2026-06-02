# src/test_gemini.py
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import GOOGLE_API_KEY  # noqa: F401

def main():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Gemini 2.5 Flash model id [web:17][web:23]
        temperature=0.7,
    )

    res = llm.invoke("Explain in two sentences who Richard Feynman was.")
    print(res.content)

if __name__ == "__main__":
    main()