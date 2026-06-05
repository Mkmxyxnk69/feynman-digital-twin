from pathlib import Path


from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


from src.persona import FEYNMAN_SYSTEM_PROMPT
from src.config import GOOGLE_API_KEY


VECTORSTORE_DIR = Path("vectorstore")




def get_retriever():
    """
    Load the Chroma vectorstore and return a retriever.
    Embeddings are already stored, so embedding_function is None.
    """
    vectordb = Chroma(
        persist_directory=str(VECTORSTORE_DIR),
        embedding_function=None,  
    )
    return vectordb.as_retriever(search_kwargs={"k": 12})



summary_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    api_key=GOOGLE_API_KEY,
)



def summarize_answer_for_memory(question: str, answer: str) -> str:
    """
    Use Gemini to compress Q + A into a short memory summary.
    The summary should capture the key physics idea in 1–2 sentences.
    """
    prompt = f"""
You are creating a short memory entry for a learning assistant.


Summarize the following Q&A in 1–2 plain sentences, focusing only on the main physics idea.


Question: {question}


Answer: {answer}


Write the summary as if you are describing what was explained, not as dialogue.
No bullet points, no markdown, just a compact description.
"""
    response = summary_llm.invoke(prompt)
    return response.content.strip()



def build_feynman_chain():
    """
    Build the main Feynman chain with:
    - Gemini 2.5 Flash as the LLM
    - Chroma retriever for RAG


    Returns:
        ask_feynman: function(user_input: str, long_term_memory_text: str = "") -> str
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        api_key=GOOGLE_API_KEY,
    )


    retriever = get_retriever()


    def ask_feynman(user_input: str, long_term_memory_text: str = "") -> str:


        docs = retriever.invoke(user_input)


        system_content = FEYNMAN_SYSTEM_PROMPT
        if long_term_memory_text:
            system_content += (
                "\n\nHere are some past things this user has asked and what you explained. "
                "Use them to personalize your answer and, when helpful, refer back to them:\n"
                f"{long_term_memory_text}"
            )


        messages = [SystemMessage(content=system_content)]


        context_text = "\n\n".join([d.page_content for d in docs])
        context_message = SystemMessage(
            content=f"Here are reference texts from Feynman's work or commentary:\n\n{context_text}"
        )
        messages.append(context_message)


        messages.append(HumanMessage(content=user_input))


        response = llm.invoke(messages)


        return response.content


    return ask_feynman
