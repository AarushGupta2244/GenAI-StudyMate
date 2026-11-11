import streamlit as st

from utils.gemini import get_gemini_service
from utils.helpers import validate_input, create_title
from database import save_study_history


st.title("✍️ AI Answer Evaluator")
st.caption("Evaluate your answers and improve your exam-writing skills.")

st.divider()


# ---------------- INPUTS ----------------

question = st.text_area(
    "Enter the Question",
    placeholder="Write the question you want to answer...",
    height=120
)

student_answer = st.text_area(
    "Enter Your Answer",
    placeholder="Write your answer here...",
    height=250
)

reference_answer = st.text_area(
    "Reference Answer (Optional)",
    placeholder="Paste a model answer or reference material if available...",
    height=180
)

col1, col2 = st.columns(2)

with col1:
    total_marks = st.slider(
        "Maximum Marks",
        min_value=1,
        max_value=20,
        value=10
    )

with col2:
    evaluation_style = st.selectbox(
        "Evaluation Style",
        [
            "University Examination",
            "Strict Evaluation",
            "Conceptual Understanding",
            "Beginner Friendly"
        ]
    )

language = st.selectbox(
    "Feedback Language",
    ["English", "Hindi", "Hinglish"]
)


# ---------------- EVALUATION ----------------

if st.button(
    "🔍 Evaluate My Answer",
    type="primary",
    use_container_width=True
):

    question_valid, question_error = validate_input(
        question,
        "question"
    )

    answer_valid, answer_error = validate_input(
        student_answer,
        "answer"
    )

    if not question_valid:
        st.warning(question_error)

    elif not answer_valid:
        st.warning(answer_error)

    else:

        prompt = f"""
        Evaluate the following student's academic answer.

        QUESTION:
        {question}

        STUDENT'S ANSWER:
        {student_answer}

        REFERENCE ANSWER:
        {reference_answer if reference_answer else "Not provided"}

        MAXIMUM MARKS:
        {total_marks}

        EVALUATION STYLE:
        {evaluation_style}

        FEEDBACK LANGUAGE:
        {language}

        Evaluate based on:
        1. Conceptual accuracy
        2. Relevance to the question
        3. Completeness
        4. Clarity and presentation
        5. Important missing points

        Return your evaluation in this structure:

        ## Marks Awarded
        Give marks in X/{total_marks} format.

        ## Overall Feedback
        Explain the quality of the answer.

        ## Strengths
        Mention what the student did correctly.

        ## Areas for Improvement
        Mention missing or incorrect points.

        ## Suggested Improvements
        Explain how to improve the answer.

        ## Improved Model Answer
        Provide a better version of the answer.

        Important rules:
        - Never award more than {total_marks} marks.
        - Be fair and academically accurate.
        - Do not give full marks without justification.
        - Do not penalize minor grammar mistakes excessively.
        - If no reference answer is supplied, evaluate using
          your academic knowledge.
        """

        try:

            with st.spinner("Evaluating your answer..."):

                gemini = get_gemini_service()

                evaluation = gemini.generate_response(
                    prompt=prompt,
                    system_instruction=(
                        "You are an experienced university professor "
                        "and academic answer evaluator. Evaluate fairly "
                        "and provide constructive feedback."
                    )
                )

            st.session_state["latest_evaluation"] = evaluation
            st.session_state["evaluation_question"] = question

            save_study_history(
                feature="Answer Evaluator",
                title=create_title(question),
                input_text=(
                    f"Question:\n{question}\n\n"
                    f"Student Answer:\n{student_answer}"
                ),
                output_text=evaluation
            )

            st.success("Answer evaluation completed!")

        except Exception as error:
            st.error(f"Unable to evaluate answer: {error}")


# ---------------- DISPLAY RESULT ----------------

if st.session_state.get("latest_evaluation"):

    st.divider()

    st.subheader("📊 Evaluation Report")

    st.markdown(
        st.session_state["latest_evaluation"]
    )

    st.download_button(
        "⬇️ Download Evaluation Report",
        data=st.session_state["latest_evaluation"],
        file_name="StudyMate_Evaluation.md",
        mime="text/markdown",
        use_container_width=True
    )