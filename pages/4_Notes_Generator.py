import streamlit as st

from utils.gemini import get_gemini_service
from utils.helpers import validate_input, create_title
from database import save_study_history


st.title("📝 AI Notes Generator")
st.caption("Generate organized, exam-ready notes on any topic.")

st.divider()

# ---------------- INPUTS ----------------

topic = st.text_input(
    "Enter your topic",
    placeholder="e.g. Operating System, DBMS, Artificial Intelligence"
)

col1, col2 = st.columns(2)

with col1:
    subject = st.text_input(
        "Subject (Optional)",
        placeholder="e.g. Computer Science"
    )

    note_style = st.selectbox(
        "Notes Format",
        [
            "Detailed Study Notes",
            "Short Revision Notes",
            "Exam-Oriented Notes",
            "Beginner-Friendly Notes"
        ]
    )

with col2:
    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Hinglish"]
    )

    detail_level = st.selectbox(
        "Detail Level",
        ["Short", "Medium", "Detailed"]
    )

additional_instructions = st.text_area(
    "Additional instructions (Optional)",
    placeholder="e.g. Include diagrams in text form, examples and important questions."
)

# ---------------- GENERATE NOTES ----------------

if st.button(
    "✨ Generate Study Notes",
    type="primary",
    use_container_width=True
):

    is_valid, error_message = validate_input(topic, "topic")

    if not is_valid:
        st.warning(error_message)

    else:

        prompt = f"""
        Create high-quality academic study notes for a college student.

        TOPIC: {topic}
        SUBJECT: {subject if subject else "Not specified"}
        FORMAT: {note_style}
        DETAIL LEVEL: {detail_level}
        LANGUAGE: {language}

        ADDITIONAL INSTRUCTIONS:
        {additional_instructions if additional_instructions else "None"}

        Follow this structure wherever relevant:

        1. Topic Introduction
        2. Important Definitions
        3. Core Concepts and Explanations
        4. Types or Classifications
        5. Working or Step-by-Step Process
        6. Examples
        7. Advantages and Disadvantages
        8. Important Exam Points
        9. Quick Revision Summary
        10. Important Questions

        Requirements:
        - Include only relevant sections.
        - Explain concepts accurately.
        - Use clear headings and bullet points.
        - Highlight important terminology.
        - Do not invent facts.
        - Make notes easy to revise before examinations.
        """

        try:

            with st.spinner("Preparing your study notes..."):

                gemini = get_gemini_service()

                notes = gemini.generate_response(
                    prompt=prompt,
                    system_instruction=(
                        "You are an expert university professor and "
                        "academic notes creator."
                    )
                )

            st.session_state["generated_notes"] = notes
            st.session_state["generated_notes_topic"] = topic

            save_study_history(
                feature="AI Notes Generator",
                title=create_title(topic),
                input_text=prompt,
                output_text=notes
            )

            st.success("Your study notes are ready!")

        except Exception as error:
            st.error(f"Unable to generate notes: {error}")


# ---------------- DISPLAY NOTES ----------------

if st.session_state.get("generated_notes"):

    st.divider()
    st.subheader(
        f"📚 Notes: {st.session_state.get('generated_notes_topic', 'Study Topic')}"
    )

    notes = st.session_state["generated_notes"]

    st.markdown(notes)

    st.download_button(
        "⬇️ Download Notes",
        data=notes,
        file_name="StudyMate_Notes.md",
        mime="text/markdown",
        use_container_width=True
    )