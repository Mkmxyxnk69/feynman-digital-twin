from pathlib import Path
import os
import pickle
from typing import List

from dotenv import load_dotenv
import google.generativeai as genai
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document


load_dotenv()

VECTORSTORE_DIR = Path("vectorstore")
BM25_DOCS_PATH = Path("bm25_docs.pkl")



genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def call_gemini(system_prompt: str, user_prompt: str) -> str:
    """
    Actual Gemini API call. Returns model's text answer.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

    full_prompt = system_prompt + "\n\n" + user_prompt

    response = model.generate_content(full_prompt)

    
    try:
        return response.text
    except AttributeError:
        return str(response)



def get_dense_retriever():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectordb = Chroma(
        collection_name="feynman_docs",
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 10})
    return retriever


def get_bm25_retriever():
    if not BM25_DOCS_PATH.exists():
        raise FileNotFoundError(
            "bm25_docs.pkl not found. Run build_vectorstore.py first."
        )
    with open(BM25_DOCS_PATH, "rb") as f:
        bm25_docs: List[Document] = pickle.load(f)

    bm25_retriever = BM25Retriever.from_documents(bm25_docs)
    bm25_retriever.k = 10
    return bm25_retriever


dense_retriever = get_dense_retriever()
bm25_retriever = get_bm25_retriever()


def hybrid_retrieve(query: str, max_candidates: int = 15) -> List[Document]:
    dense_docs = dense_retriever.invoke(query)
    sparse_docs = bm25_retriever.invoke(query)

    seen = set()
    candidates: List[Document] = []
    for doc in dense_docs + sparse_docs:
        key = (doc.metadata.get("source", ""), doc.page_content)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(doc)
        if len(candidates) >= max_candidates:
            break
    return candidates



def rerank_with_llm(query: str, candidates: List[Document], top_k: int = 5) -> List[Document]:
    """
    Placeholder: currently just returns first top_k candidates.
    You can later replace this with a Gemini-based reranker if you want.
    """
    return candidates[:top_k]


def build_context(reranked_docs: List[Document]) -> str:
    parts = []
    for i, doc in enumerate(reranked_docs):
        parts.append(f"[Doc {i}]\n{doc.page_content}\n")
    return "\n\n".join(parts)


def ask_feynman(question: str) -> str:
    """
    Hybrid retrieval + (optional) rerank + Gemini call
    with Feynman persona + retrieved context.
    """

    candidates = hybrid_retrieve(question, max_candidates=15)
    selected_docs = rerank_with_llm(question, candidates, top_k=5)
    context = build_context(selected_docs)

    system_prompt = (
        "You are a digital twin of Richard Feynman. "
        "You explain physics with simple language, vivid analogies, and curiosity. "
        "You are honest about uncertainty, and you sometimes ask the student questions "
        "to make them think. Stay concise but clear."
    )

    user_prompt = (
        "You are answering a student's question using the notes below.\n\n"
        "=== Retrieved notes (Feynman-style sources) ===\n"
        f"{context}\n"
        "=== End of notes ===\n\n"
        f"Student's question: {question}\n\n"
        "Using ONLY the information that can be reasonably inferred from the notes above "
        "and your general physics knowledge, explain the answer in Richard Feynman's style. "
        "Prefer everyday examples and ask the student at least one short question in the explanation "
        "to keep it interactive."
    )

    answer = call_gemini(system_prompt, user_prompt)
    return answer


def main():
    print("Type your question (or 'exit' to quit):")
    while True:
        q = input("> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        ans = ask_feynman(q)
        print("\n" + ans + "\n")


if __name__ == "__main__":
    main()