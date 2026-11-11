import streamlit as st

from utils.gemini import get_gemini_service
from utils.pdf_processor import extract_pdf_text, split_text_into_chunks
from utils.helpers import count_words, format_timestamp
from database import save_study_history


st.title("📄 PDF Summarizer")
st.caption("Turn lengthy PDF documents into clear and structured summaries.")

st.divider()

# ---------------- PDF UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload your PDF document",
    type=["pdf"],
    help="Maximum file size: 20 MB"
)

# ---------------- SUMMARY OPTIONS ----------------

col1, col2 = st.columns(2)

with col1:
    summary_style = st.selectbox(
        "Summary Style",
        [
            "Detailed Summary",
            "Short Summary",
            "Exam-Oriented Summary",
            "Chapter-wise Summary"
        ]
    )

with col2:
    language = st.selectbox(
        "Output Language",
        ["English", "Hindi", "Hinglish"]
    )

# ---------------- PROCESS PDF ----------------

if uploaded_file:

    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > 20:
        st.error("File size exceeds the 20 MB limit.")

    else:
        st.success(f"Uploaded: {uploaded_file.name}")

        if st.button("✨ Generate Summary", type="primary",
                     use_container_width=True):

            try:
                with st.spinner("Reading your PDF..."):
                    pdf_text, total_pages = extract_pdf_text(uploaded_file)

                chunks = split_text_into_chunks(
                    pdf_text,
                    chunk_size=12000,
                    overlap=500
                )

                st.info(
                    f"PDF contains {total_pages} pages and "
                    f"{count_words(pdf_text)} words."
                )

                gemini = get_gemini_service()

                style_instructions = {
                    "Detailed Summary": (
                        "Create a comprehensive summary with clear headings, "
                        "explanations and examples."
                    ),
                    "Short Summary": (
                        "Create a concise summary covering only the most "
                        "important information."
                    ),
                    "Exam-Oriented Summary": (
                        "Create exam preparation notes. Include definitions, "
                        "important concepts, key points and likely exam topics."
                    ),
                    "Chapter-wise Summary": (
                        "Organize the summary chapter-wise or section-wise "
                        "where the document structure allows it."
                    )
                }

                summaries = []

                progress = st.progress(0)

                for index, chunk in enumerate(chunks):

                    prompt = f"""
                    Summarize the following part of a PDF document.

                    Instructions:
                    - {style_instructions[summary_style]}
                    - Write the output in {language}.
                    - Preserve important facts, names, definitions and numbers.
                    - Do not add information that is not present in the text.
                    - Make the summary easy for a college student to understand.

                    Document: {uploaded_file.name}
                    Part: {index + 1} of {len(chunks)}

                    DOCUMENT TEXT:
                    {chunk}
                    """

                    part_summary = gemini.generate_response(
                        prompt=prompt,
                        system_instruction=(
                            "You are an expert academic PDF summarization assistant."
                        )
                    )

                    summaries.append(part_summary)

                    progress.progress(
                        (index + 1) / len(chunks)
                    )

                # Combine summaries when multiple chunks exist
                if len(summaries) == 1:
                    final_summary = summaries[0]

                else:
                    combined_prompt = f"""
                    Combine the following summaries into one well-organized
                    final summary.

                    Requirements:
                    - Write in {language}.
                    - Remove repeated information.
                    - Preserve all important concepts.
                    - Use headings, bullet points and clear explanations.
                    - End with key takeaways.

                    SUMMARIES:
                    {"\n\n".join(summaries)}
                    """

                    with st.spinner("Preparing your final summary..."):
                        final_summary = gemini.generate_response(
                            prompt=combined_prompt,
                            system_instruction=(
                                "You are an expert academic editor."
                            )
                        )

                # Display and save result
                st.session_state["latest_pdf_summary"] = final_summary
                st.session_state["latest_pdf_name"] = uploaded_file.name

                save_study_history(
                    feature="PDF Summarizer",
                    title=uploaded_file.name,
                    input_text=(
                        f"PDF: {uploaded_file.name}\n"
                        f"Pages: {total_pages}"
                    ),
                    output_text=final_summary
                )

                st.success("Your PDF summary is ready!")

            except Exception as error:
                st.error(f"Unable to summarize PDF: {error}")


# ---------------- DISPLAY SUMMARY ----------------

if st.session_state.get("latest_pdf_summary"):

    st.divider()
    st.subheader("📚 Generated Summary")

    st.markdown(st.session_state["latest_pdf_summary"])

    st.download_button(
        label="⬇️ Download Summary",
        data=st.session_state["latest_pdf_summary"],
        file_name="StudyMate_PDF_Summary.txt",
        mime="text/plain",
        use_container_width=True
    )