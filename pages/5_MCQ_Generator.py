import streamlit as st
import json
import re

from utils.gemini import get_gemini_service
from utils.helpers import validate_input, create_title
from database import save_study_history


st.title("❓ AI MCQ Generator")
st.caption("Generate topic-based multiple-choice questions for practice.")

st.divider()


# ---------------- INPUTS ----------------

topic = st.text_input(
    "Enter Topic",
    placeholder="e.g. Python Programming, Computer Networks, DBMS"
)

col1, col2 = st.columns(2)

with col1:
    number_of_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=30,
        value=10
    )

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Easy", "Medium", "Hard", "Mixed"]
    )

with col2:
    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Hinglish"]
    )

    include_explanations = st.checkbox(
        "Include Answer Explanations",
        value=True
    )

additional_context = st.text_area(
    "Additional Instructions (Optional)",
    placeholder="e.g. Focus on university examination questions."
)


# ---------------- GENERATE MCQS ----------------

if st.button(
    "✨ Generate MCQs",
    type="primary",
    use_container_width=True
):

    is_valid, error_message = validate_input(topic, "topic")

    if not is_valid:
        st.warning(error_message)

    else:

        prompt = f"""
        Generate exactly {number_of_questions} multiple-choice questions.

        Topic: {topic}
        Difficulty: {difficulty}
        Language: {language}
        Additional instructions: {additional_context}

        Each question must have:
        - One question
        - Exactly four options
        - One correct answer
        - An explanation

        Return ONLY valid JSON in this exact structure:

        {{
            "questions": [
                {{
                    "question": "Question text",
                    "options": {{
                        "A": "Option A",
                        "B": "Option B",
                        "C": "Option C",
                        "D": "Option D"
                    }},
                    "correct_answer": "A",
                    "explanation": "Explanation of the correct answer"
                }}
            ]
        }}

        Rules:
        - correct_answer must be A, B, C or D.
        - Ensure factual accuracy.
        - Avoid duplicate questions.
        - Do not include Markdown code fences.
        """

        try:

            with st.spinner("Generating your MCQs..."):

                gemini = get_gemini_service()

                response = gemini.generate_response(
                    prompt=prompt,
                    system_instruction=(
                        "You are an expert academic question paper creator. "
                        "Generate accurate and educational MCQs."
                    )
                )

                # Extract JSON safely
                cleaned_response = re.sub(
                    r"^```(?:json)?\s*|\s*```$",
                    "",
                    response.strip(),
                    flags=re.IGNORECASE
                )

                mcq_data = json.loads(cleaned_response)

                questions = mcq_data.get("questions", [])

                if not questions:
                    raise ValueError("No questions were generated.")

                # Validate question structure
                for question in questions:

                    if not all(
                        key in question
                        for key in [
                            "question",
                            "options",
                            "correct_answer",
                            "explanation"
                        ]
                    ):
                        raise ValueError(
                            "AI returned an incomplete question."
                        )

                    if set(question["options"].keys()) != {
                        "A", "B", "C", "D"
                    }:
                        raise ValueError(
                            "A question does not have four valid options."
                        )

                    if question["correct_answer"] not in {
                        "A", "B", "C", "D"
                    }:
                        raise ValueError(
                            "Invalid correct answer received."
                        )

                st.session_state["generated_mcqs"] = questions
                st.session_state["mcq_topic"] = topic
                st.session_state["mcq_show_answers"] = False

                save_study_history(
                    feature="MCQ Generator",
                    title=create_title(topic),
                    input_text=prompt,
                    output_text=json.dumps(
                        mcq_data,
                        ensure_ascii=False,
                        indent=2
                    )
                )

            st.success(
                f"{len(questions)} MCQs generated successfully!"
            )

        except json.JSONDecodeError:
            st.error(
                "AI returned an invalid question format. Please try again."
            )

        except Exception as error:
            st.error(f"Unable to generate MCQs: {error}")


# ---------------- DISPLAY QUESTIONS ----------------

if st.session_state.get("generated_mcqs"):

    questions = st.session_state["generated_mcqs"]

    st.divider()

    st.subheader(
        f"📚 MCQs: {st.session_state.get('mcq_topic', 'Practice')}"
    )

    st.caption(f"Total Questions: {len(questions)}")

    if st.button("Show All Correct Answers"):
        st.session_state["mcq_show_answers"] = True

    for index, question in enumerate(questions):

        with st.container(border=True):

            st.markdown(
                f"**Q{index + 1}. {question['question']}**"
            )

            for option_key in ["A", "B", "C", "D"]:

                st.markdown(
                    f"**{option_key}.** {question['options'][option_key]}"
                )

            if st.session_state.get("mcq_show_answers"):

                correct = question["correct_answer"]

                st.success(
                    f"Correct Answer: {correct}. "
                    f"{question['options'][correct]}"
                )

                if include_explanations:
                    st.info(question["explanation"])