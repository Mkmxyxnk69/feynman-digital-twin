from pathlib import Path
import pickle

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv() 

DATA_DIR = Path("data")
VECTORSTORE_DIR = Path("vectorstore")
BM25_DOCS_PATH = Path("bm25_docs.pkl")


def load_documents():
    docs = []
    for file in DATA_DIR.glob("*.txt"):
        loader = TextLoader(str(file), encoding="utf-8")
        docs.extend(loader.load())
    return docs


def build_vectorstore():
    print("Loading documents...")
    docs = load_documents()
    if not docs:
        raise ValueError("No .txt files found in data/ folder.")

    print(f"Loaded {len(docs)} documents. Splitting into chunks...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    split_docs = splitter.split_documents(docs)
    print(f"Created {len(split_docs)} chunks.")

    print("Creating embeddings and building Chroma vectorstore...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    VECTORSTORE_DIR.mkdir(exist_ok=True)

    vectordb = Chroma(
        collection_name="feynman_docs",
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )

    vectordb.delete_collection()
    vectordb = Chroma(
        collection_name="feynman_docs",
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )

    vectordb.add_documents(split_docs)
    print("Vectorstore built and saved to 'vectorstore/'.")

    with open(BM25_DOCS_PATH, "wb") as f:
        pickle.dump(split_docs, f)
    print(f"Saved BM25 documents for sparse retrieval to '{BM25_DOCS_PATH}'.")
    print("Done.")

def main():
    build_vectorstore()

if __name__ == "__main__":
    main()