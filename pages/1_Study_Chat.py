import streamlit as st
import uuid

from utils.gemini import get_gemini_service
from database import save_chat_message


# ---------------- PAGE HEADER ----------------

st.title("💬 AI Study Chat")
st.caption("Ask questions, understand concepts and learn with your AI tutor.")

st.divider()


# ---------------- SESSION INITIALIZATION ----------------

if "study_chat_session" not in st.session_state:
    st.session_state.study_chat_session = str(uuid.uuid4())

if "study_chat_messages" not in st.session_state:
    st.session_state.study_chat_messages = []

if "study_chat_greeting" not in st.session_state:
    st.session_state.study_chat_greeting = True


# ---------------- SIDEBAR OPTIONS ----------------

with st.sidebar:
    st.markdown("### 💬 Chat Controls")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.study_chat_session = str(uuid.uuid4())
        st.session_state.study_chat_messages = []
        st.session_state.study_chat_greeting = True
        st.rerun()

    st.divider()

    st.markdown("### 🎯 Study Mode")

    study_mode = st.selectbox(
        "Choose response style",
        [
            "Beginner Friendly",
            "Detailed Explanation",
            "Exam Preparation",
            "Short and Precise"
        ]
    )


# ---------------- SYSTEM INSTRUCTIONS ----------------

mode_instructions = {
    "Beginner Friendly": (
        "Explain concepts in very simple language with easy examples."
    ),
    "Detailed Explanation": (
        "Give detailed explanations with examples and step-by-step reasoning."
    ),
    "Exam Preparation": (
        "Explain concepts in an exam-oriented manner. Highlight important "
        "definitions, points and likely examination questions."
    ),
    "Short and Precise": (
        "Give concise, accurate answers without unnecessary details."
    )
}

system_instruction = f"""
You are StudyMate AI, a helpful and knowledgeable academic tutor.

Your goal is to help university and college students understand their subjects.

Follow these rules:
1. Explain concepts clearly and accurately.
2. Use headings and bullet points wherever useful.
3. Include practical examples when appropriate.
4. For programming questions, provide properly formatted code.
5. If a question is unclear, ask for clarification.
6. Never invent facts or pretend to know something you do not know.

Current response style:
{mode_instructions[study_mode]}
"""


# ---------------- WELCOME MESSAGE ----------------

if st.session_state.study_chat_greeting:
    st.info(
        "👋 Hello! I am your StudyMate AI tutor. "
        "Ask me anything about programming, mathematics, computer science "
        "or any other academic subject."
    )

    st.session_state.study_chat_greeting = False


# ---------------- DISPLAY CHAT HISTORY ----------------

for message in st.session_state.study_chat_messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------- CHAT INPUT ----------------

user_prompt = st.chat_input(
    "Ask your study question here..."
)


# ---------------- GENERATE STREAMING RESPONSE ----------------

if user_prompt:

    # Save user message
    st.session_state.study_chat_messages.append({
        "role": "user",
        "content": user_prompt
    })

    save_chat_message(
        st.session_state.study_chat_session,
        "user",
        user_prompt
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Prepare conversation context
    conversation_context = []

    for message in st.session_state.study_chat_messages[-12:]:
        conversation_context.append(
            f"{message['role'].upper()}: {message['content']}"
        )

    prompt = "\n\n".join(conversation_context)

    # Generate streaming response
    with st.chat_message("assistant"):

        try:
            gemini = get_gemini_service()

            response_placeholder = st.empty()
            full_response = ""

            with st.spinner("Connecting to StudyMate AI..."):

                response_stream = gemini.generate_stream(
                    prompt=prompt,
                    system_instruction=system_instruction
                )

                for text_chunk in response_stream:
                    full_response += text_chunk

                    response_placeholder.markdown(
                        full_response + "▌"
                    )

            if full_response.strip():

                response_placeholder.markdown(full_response)

                st.session_state.study_chat_messages.append({
                    "role": "assistant",
                    "content": full_response
                })

                save_chat_message(
                    st.session_state.study_chat_session,
                    "assistant",
                    full_response
                )

            else:
                st.error("AI returned an empty response.")

        except Exception as error:
            st.error(str(error))