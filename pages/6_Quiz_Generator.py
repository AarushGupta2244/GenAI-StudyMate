import streamlit as st
import json
import re

from utils.gemini import get_gemini_service
from utils.helpers import validate_input, create_title
from database import save_study_history, save_quiz_result


st.title("🎯 Interactive Quiz Generator")
st.caption("Test your knowledge and track your learning progress.")

st.divider()


# ---------------- INPUTS ----------------

topic = st.text_input(
    "Enter Quiz Topic",
    placeholder="e.g. Python, Operating Systems, DBMS"
)

col1, col2 = st.columns(2)

with col1:
    number_of_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=20,
        value=10
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard", "Mixed"]
    )

with col2:
    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Hinglish"]
    )


# ---------------- GENERATE QUIZ ----------------

if st.button(
    "🚀 Generate Quiz",
    type="primary",
    use_container_width=True
):

    is_valid, error_message = validate_input(topic, "topic")

    if not is_valid:
        st.warning(error_message)

    else:

        prompt = f"""
        Create exactly {number_of_questions} educational MCQs.

        Topic: {topic}
        Difficulty: {difficulty}
        Language: {language}

        Return ONLY valid JSON in this format:

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
                    "explanation": "Explanation"
                }}
            ]
        }}

        Rules:
        - Exactly four options per question.
        - Only one correct answer.
        - correct_answer must be A, B, C or D.
        - Avoid duplicate questions.
        - Ensure factual accuracy.
        - Do not include Markdown code fences.
        """

        try:

            with st.spinner("Preparing your quiz..."):

                gemini = get_gemini_service()

                response = gemini.generate_response(
                    prompt=prompt,
                    system_instruction=(
                        "You are an expert university examiner. "
                        "Create accurate and educational quizzes."
                    )
                )

                cleaned_response = re.sub(
                    r"^```(?:json)?\s*|\s*```$",
                    "",
                    response.strip(),
                    flags=re.IGNORECASE
                )

                quiz_data = json.loads(cleaned_response)

                questions = quiz_data.get("questions", [])

                if len(questions) != number_of_questions:
                    raise ValueError(
                        f"Expected {number_of_questions} questions, "
                        f"but received {len(questions)}."
                    )

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
                        raise ValueError("Incomplete question received.")

                    if set(question["options"].keys()) != {
                        "A", "B", "C", "D"
                    }:
                        raise ValueError("Invalid question options.")

                    if question["correct_answer"] not in {
                        "A", "B", "C", "D"
                    }:
                        raise ValueError("Invalid correct answer.")

                st.session_state["active_quiz"] = {
                    "topic": topic,
                    "questions": questions,
                    "submitted": False,
                    "answers": {}
                }

                save_study_history(
                    feature="Quiz Generator",
                    title=create_title(topic),
                    input_text=prompt,
                    output_text=json.dumps(
                        quiz_data,
                        ensure_ascii=False,
                        indent=2
                    )
                )

            st.success("Your quiz is ready!")
            st.rerun()

        except json.JSONDecodeError:
            st.error("Invalid response format. Please generate the quiz again.")

        except Exception as error:
            st.error(f"Unable to generate quiz: {error}")


# ---------------- DISPLAY ACTIVE QUIZ ----------------

quiz = st.session_state.get("active_quiz")

if quiz:

    st.divider()

    st.subheader(f"📝 Quiz: {quiz['topic']}")

    questions = quiz["questions"]

    st.write(f"Total Questions: **{len(questions)}**")

    if not quiz["submitted"]:

        with st.form("quiz_attempt_form"):

            selected_answers = {}

            for index, question in enumerate(questions):

                st.markdown(f"### Q{index + 1}. {question['question']}")

                selected_answers[index] = st.radio(
                    "Choose your answer:",
                    options=["A", "B", "C", "D"],
                    format_func=lambda option, q=question: (
                        f"{option}. {q['options'][option]}"
                    ),
                    key=f"quiz_answer_{index}",
                    index=None
                )

                st.divider()

            submitted = st.form_submit_button(
                "Submit Quiz",
                type="primary",
                use_container_width=True
            )

        if submitted:

            unanswered = [
                index + 1
                for index, answer in selected_answers.items()
                if answer is None
            ]

            if unanswered:

                st.warning(
                    "Please answer all questions before submitting. "
                    f"Unanswered: {', '.join(map(str, unanswered))}"
                )

            else:

                correct_answers = sum(
                    1
                    for index, question in enumerate(questions)
                    if selected_answers[index] == question["correct_answer"]
                )

                score = (
                    correct_answers / len(questions)
                ) * 100

                quiz["answers"] = selected_answers
                quiz["submitted"] = True
                quiz["correct_answers"] = correct_answers
                quiz["score"] = score

                save_quiz_result(
                    topic=quiz["topic"],
                    total_questions=len(questions),
                    correct_answers=correct_answers
                )

                st.session_state["active_quiz"] = quiz

                st.rerun()

    else:

        # ---------------- QUIZ RESULTS ----------------

        correct_answers = quiz["correct_answers"]
        score = quiz["score"]

        st.subheader("🏆 Your Quiz Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Score", f"{score:.1f}%")

        with col2:
            st.metric(
                "Correct Answers",
                f"{correct_answers}/{len(questions)}"
            )

        with col3:
            st.metric(
                "Incorrect Answers",
                len(questions) - correct_answers
            )

        if score >= 80:
            st.success("Excellent performance! Keep it up.")

        elif score >= 60:
            st.info("Good work! A little more practice will help.")

        else:
            st.warning("Keep practising. You can improve!")

        st.progress(score / 100)

        st.divider()
        st.subheader("📖 Answer Review")

        for index, question in enumerate(questions):

            selected = quiz["answers"][index]
            correct = question["correct_answer"]

            with st.container(border=True):

                st.markdown(
                    f"**Q{index + 1}. {question['question']}**"
                )

                st.write(
                    f"Your Answer: {selected}. "
                    f"{question['options'][selected]}"
                )

                st.write(
                    f"Correct Answer: {correct}. "
                    f"{question['options'][correct]}"
                )

                if selected == correct:
                    st.success("Correct!")
                else:
                    st.error("Incorrect")

                st.info(question["explanation"])

        if st.button(
            "🔄 Start New Quiz",
            type="primary",
            use_container_width=True
        ):
            del st.session_state["active_quiz"]
            st.rerun()