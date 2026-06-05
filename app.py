
import streamlit as st
from datetime import datetime
import os
import subprocess
import speech_recognition as sr

from src.feynman_chain import build_feynman_chain, summarize_answer_for_memory
from memory_store import add_memory, get_recent_memories, load_memories

USER_ID = "default_user"


def text_to_speech_mac(text: str) -> None:
    """
    Speak text aloud using macOS 'say' command.
    """
    if not text:
        return

    subprocess.run(
        ["say", text],
        check=True
    )


def _human_time_label(ts_str: str) -> str:
    """
    Convert ISO timestamp string to a human-friendly label.
    Example outputs: 'today', 'yesterday', 'earlier this week', or a date string.
    """
    try:
        ts = datetime.fromisoformat(ts_str)
    except Exception:
        return ts_str  

    now = datetime.now()
    delta = now - ts
    days = delta.days

    if days == 0:
        return "today"
    elif days == 1:
        return "yesterday"
    elif days < 7:
        return "earlier this week"
    elif days < 30:
        return "earlier this month"
    else:
        return ts.strftime("%Y-%m-%d")


def build_long_term_memory_text(user_id: str = USER_ID, k: int = 5) -> str:
    """
    Turn recent long-term memories into a short text block
    that we inject into the system prompt, with human-friendly
    time phrases.
    """
    mems = get_recent_memories(user_id=user_id, k=k)
    if not mems:
        return ""

    lines = []
    for m in mems:
        label = _human_time_label(m["timestamp"])
        lines.append(
            f"- {label}, the user asked: \"{m['question']}\". "
            f"You explained: {m['answer_summary']}"
        )
    return "\n".join(lines)


def run_voice_feynman():
    """
    Record a question from the microphone, send it to the Feynman twin,
    and speak back the answer using macOS 'say'.
    """

    os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")

    r = sr.Recognizer()
    feynman_chain = build_feynman_chain()

    with sr.Microphone() as source:
        st.write("🎤 Listening... please speak")
        audio = r.listen(source)

    st.write("Recognizing...")

    try:
        question = r.recognize_google(audio)
    except sr.UnknownValueError:
        st.warning("Could not understand audio. Please try speaking more clearly or closer to the mic.")
        return
    except sr.RequestError as e:
        st.error(f"Could not reach speech recognition service: {e}")
        return

    st.write(f"You said: **{question}**")

    long_term_memory_text = build_long_term_memory_text(USER_ID, k=5)
    answer = feynman_chain(
        question,
        long_term_memory_text=long_term_memory_text,
    )

    st.write("Feynman says:")
    st.markdown(answer)


    try:
        text_to_speech_mac(answer)
    except Exception as e:
        st.warning(f"Could not speak answer: {e}")

    answer_summary = summarize_answer_for_memory(question, answer)
    add_memory(question, answer_summary, user_id=USER_ID)


st.set_page_config(page_title="Feynman Digital Twin", page_icon="🧠")

if "feynman_chain" not in st.session_state:
    st.session_state.feynman_chain = build_feynman_chain()

feynman = st.session_state.feynman_chain

with st.sidebar:
    st.header("About this app")
    st.write(
        "Digital Twin of Richard Feynman.\n"
        "Built with LangChain, Gemini 2.5 Flash, and Chroma."
    )
    st.write("Try asking about quantum mechanics, atoms, or electromagnetism.")

    if st.sidebar.button("Reset conversation"):
        st.session_state.messages = []
        st.session_state.feynman_chain = build_feynman_chain()
        st.success("Conversation reset!")

st.title("Richard Feynman – Digital Twin")
st.write(
    "Ask questions about physics or related topics, and get explanations in a Feynman-like style."
)

chat_tab, voice_tab, memory_tab = st.tabs(
    ["Chat", "Voice", "Memory"]
)

with chat_tab:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)

    user_input = st.chat_input("Ask Feynman a question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking like Feynman..."):
                long_term_memory_text = build_long_term_memory_text(USER_ID, k=5)
                answer = feynman(
                    user_input,
                    long_term_memory_text=long_term_memory_text,
                )
                st.markdown(answer)

                if st.button("🔊 Read this answer aloud", key=f"tts_{len(st.session_state.messages)}"):
                    try:
                        text_to_speech_mac(answer)
                    except Exception as e:
                        st.warning(f"Could not speak answer: {e}")

        st.session_state.messages.append({"role": "assistant", "content": answer})

        answer_summary = summarize_answer_for_memory(user_input, answer)
        add_memory(user_input, answer_summary, user_id=USER_ID)

with voice_tab:
    st.subheader("Voice interaction")

    st.write(
        "Click the button below, ask your question by speaking into the microphone, "
        "and Feynman's digital twin will answer you in text and speech."
    )

    if st.button("🎤 Ask by voice"):
        run_voice_feynman()

with memory_tab:
    st.subheader("Long-term memory view")

    all_mems = load_memories()
    user_mems = all_mems.get(USER_ID, [])

    if not user_mems:
        st.info("No memories stored yet for this user.")
    else:
        with st.expander("Raw memories JSON"):
            st.json(user_mems)

        st.markdown("### Recent memories")
        for m in reversed(user_mems):
            with st.expander(f"{m['timestamp']}  —  {m['question']}"):
                st.write(f"**Question:** {m['question']}")
                st.write(f"**Summary:** {m['answer_summary']}")