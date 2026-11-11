import streamlit as st
import uuid
import re

from utils.gemini import get_gemini_service
from utils.pdf_processor import extract_pdf_text, split_text_into_chunks
from database import save_chat_message


st.title("🔍 Chat with PDF")
st.caption("Upload a document and ask questions about its contents.")

st.divider()


# ---------------- SESSION STATE ----------------

if "pdf_chat_session" not in st.session_state:
    st.session_state.pdf_chat_session = str(uuid.uuid4())

if "pdf_chat_messages" not in st.session_state:
    st.session_state.pdf_chat_messages = []

if "pdf_chat_text" not in st.session_state:
    st.session_state.pdf_chat_text = ""

if "pdf_chat_chunks" not in st.session_state:
    st.session_state.pdf_chat_chunks = []

if "pdf_chat_filename" not in st.session_state:
    st.session_state.pdf_chat_filename = ""


# ---------------- PDF UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"],
    help="Maximum file size: 20 MB"
)

if uploaded_file:

    if uploaded_file.size > 20 * 1024 * 1024:
        st.error("PDF size must be below 20 MB.")

    else:
        if uploaded_file.name != st.session_state.pdf_chat_filename:

            try:
                with st.spinner("Reading your PDF..."):

                    pdf_text, total_pages = extract_pdf_text(uploaded_file)

                    chunks = split_text_into_chunks(
                        pdf_text,
                        chunk_size=5000,
                        overlap=400
                    )

                    st.session_state.pdf_chat_text = pdf_text
                    st.session_state.pdf_chat_chunks = chunks
                    st.session_state.pdf_chat_filename = uploaded_file.name
                    st.session_state.pdf_chat_messages = []
                    st.session_state.pdf_chat_session = str(uuid.uuid4())

                st.success(
                    f"PDF ready! {total_pages} pages processed."
                )

            except Exception as error:
                st.error(f"Unable to read PDF: {error}")


# ---------------- RELEVANT TEXT SEARCH ----------------

def find_relevant_chunks(question, chunks, top_k=4):

    def tokenize(text):
        return set(
            re.findall(r"\b[a-zA-Z0-9]{3,}\b", text.lower())
        )

    question_words = tokenize(question)

    if not question_words:
        return chunks[:top_k]

    scored_chunks = []

    for index, chunk in enumerate(chunks):

        chunk_words = tokenize(chunk)

        overlap = len(question_words.intersection(chunk_words))

        scored_chunks.append((overlap, index, chunk))

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True
    )

    selected = [
        chunk
        for score, index, chunk in scored_chunks[:top_k]
        if score > 0
    ]

    return selected if selected else chunks[:top_k]


# ---------------- CHAT INTERFACE ----------------

if st.session_state.pdf_chat_text:

    st.success(
        f"📄 Currently chatting with: "
        f"**{st.session_state.pdf_chat_filename}**"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        st.caption(
            f"{len(st.session_state.pdf_chat_chunks)} text sections available"
        )

    with col2:
        if st.button("Clear Chat"):
            st.session_state.pdf_chat_messages = []
            st.session_state.pdf_chat_session = str(uuid.uuid4())
            st.rerun()

    st.divider()

    # Display previous messages
    for message in st.session_state.pdf_chat_messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User question
    question = st.chat_input(
        "Ask anything about your PDF..."
    )

    if question:

        st.session_state.pdf_chat_messages.append({
            "role": "user",
            "content": question
        })

        save_chat_message(
            st.session_state.pdf_chat_session,
            "user",
            question
        )

        with st.chat_message("user"):
            st.markdown(question)

        relevant_chunks = find_relevant_chunks(
            question,
            st.session_state.pdf_chat_chunks
        )

        context = "\n\n".join(relevant_chunks)

        prompt = f"""
        Answer the user's question using the PDF context below.

        Rules:
        1. Base your answer on the supplied PDF context.
        2. Do not invent information.
        3. If the answer is not available in the supplied context,
           clearly say that it could not be found in the relevant
           extracted sections of the PDF.
        4. Explain the answer in simple student-friendly language.
        5. Use headings and bullet points when useful.

        PDF NAME:
        {st.session_state.pdf_chat_filename}

        PDF CONTEXT:
        {context}

        CONVERSATION:
        {chr(10).join(
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.pdf_chat_messages[-6:]
        )}

        USER QUESTION:
        {question}
        """

        with st.chat_message("assistant"):

            with st.spinner("Searching your PDF and preparing an answer..."):

                try:
                    gemini = get_gemini_service()

                    answer = gemini.generate_response(
                        prompt=prompt,
                        system_instruction=(
                            "You are StudyMate, an academic assistant "
                            "specialized in answering questions from documents."
                        )
                    )

                    st.markdown(answer)

                    st.session_state.pdf_chat_messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                    save_chat_message(
                        st.session_state.pdf_chat_session,
                        "assistant",
                        answer
                    )

                except Exception as error:
                    st.error(f"Unable to generate answer: {error}")

else:

    st.info(
        "👆 Upload a PDF to start asking questions about your document."
    )