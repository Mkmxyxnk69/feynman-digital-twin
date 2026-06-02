# src/test_feynman_chain.py

from src.feynman_chain import build_feynman_chain

def main():
    feynman = build_feynman_chain()
    answer = feynman("Can you explain what an atom is in simple words?")
    print(answer)

if __name__ == "__main__":
    main()