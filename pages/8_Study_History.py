import streamlit as st

from database import get_study_history, get_quiz_results
from utils.helpers import format_timestamp, truncate_text


st.title("📚 Study History")
st.caption("Review your previous learning activities and quiz performance.")

st.divider()


# ---------------- FETCH DATA ----------------

study_history = get_study_history(limit=100)
quiz_results = get_quiz_results(limit=50)


# ---------------- TABS ----------------

tab1, tab2 = st.tabs([
    "📖 Study Activities",
    "🏆 Quiz Performance"
])


# ---------------- STUDY ACTIVITIES ----------------

with tab1:

    st.subheader("Your Learning Activities")

    if study_history:

        search_query = st.text_input(
            "🔍 Search activities",
            placeholder="Search by title or feature..."
        )

        filtered_history = [
            activity for activity in study_history
            if (
                search_query.lower() in activity["title"].lower()
                or search_query.lower() in activity["feature"].lower()
            )
        ]

        st.caption(
            f"Showing {len(filtered_history)} of {len(study_history)} activities"
        )

        if filtered_history:

            for activity in filtered_history:

                with st.expander(
                    f"📄 {activity['title']} — {activity['feature']}"
                ):

                    st.caption(
                        f"Created: {format_timestamp(activity['created_at'])}"
                    )

                    st.markdown("**Input / Request**")

                    st.write(
                        truncate_text(
                            activity["input_text"] or "",
                            1000
                        )
                    )

                    st.divider()

                    st.markdown("**Generated Output**")

                    output_text = activity["output_text"] or ""

                    st.markdown(output_text)

                    st.download_button(
                        label="⬇️ Download Result",
                        data=output_text,
                        file_name=f"StudyMate_Activity_{activity['id']}.md",
                        mime="text/markdown",
                        key=f"download_activity_{activity['id']}"
                    )

        else:
            st.info("No matching activities found.")

    else:
        st.info(
            "Your study history is empty. Start using StudyMate's AI tools "
            "to see your activities here."
        )


# ---------------- QUIZ PERFORMANCE ----------------

with tab2:

    st.subheader("Your Quiz Results")

    if quiz_results:

        total_attempts = len(quiz_results)

        average_score = sum(
            result["score"] for result in quiz_results
        ) / total_attempts

        best_score = max(
            result["score"] for result in quiz_results
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Quizzes", total_attempts)

        with col2:
            st.metric("Average Score", f"{average_score:.1f}%")

        with col3:
            st.metric("Best Score", f"{best_score:.1f}%")

        st.divider()

        for index, result in enumerate(quiz_results):

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{result['topic']}**")

                    st.caption(
                        format_timestamp(result["created_at"])
                    )

                with col2:
                    st.metric(
                        "Score",
                        f"{result['score']:.1f}%"
                    )

                st.progress(
                    max(0.0, min(1.0, result["score"] / 100))
                )

                st.write(
                    f"Correct Answers: **{result['correct_answers']}** "
                    f"out of **{result['total_questions']}**"
                )

    else:
        st.info(
            "No quiz attempts yet. Complete an interactive quiz "
            "to track your performance here."
        )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "🎓 GenAI StudyMate | Your learning journey, all in one place."
)