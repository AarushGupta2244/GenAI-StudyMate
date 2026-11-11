import streamlit as st

from config import APP_NAME, APP_TAGLINE, APP_VERSION
from database import (
    initialize_database,
    get_study_history,
    get_quiz_results
)
from utils.helpers import format_timestamp, truncate_text


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- DATABASE INITIALIZATION ----------------

initialize_database()


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

    /* Main Application */

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    [data-testid="stHeader"] {
        background-color: var(--background-color);
    }


    /* Hide unwanted app navigation label */

    [data-testid="stSidebarNav"] ul li:first-child {
        display: none;
    }


    /* Hero Section */

    .hero {
        padding: 35px;
        border-radius: 20px;
        background: linear-gradient(120deg, #312E81, #6D28D9);
        margin-bottom: 28px;
    }

    .hero h1 {
        color: #FFFFFF !important;
        font-size: 38px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #E0E7FF !important;
        font-size: 17px;
    }


    /* Feature Cards */

    .feature-card {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--border-color, #64748b);
        padding: 22px;
        border-radius: 15px;
        min-height: 155px;
        margin-bottom: 15px;
    }

    .feature-card h3 {
        color: var(--primary-color);
        font-size: 19px;
        margin-bottom: 8px;
    }

    .feature-card p {
        color: var(--text-color);
        font-size: 14px;
    }


    /* Section Titles */

    .section-title {
        color: var(--text-color);
        font-size: 25px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
    }


    /* Metrics */

    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--border-color, #64748b);
        padding: 18px;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: var(--text-color) !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: var(--text-color) !important;
    }


    /* Recent Activity */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stVerticalBlockBorderWrapper"] strong {
        color: var(--text-color);
    }


    /* Sidebar */

    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: var(--text-color);
    }


    /* Footer */

    .footer-text {
        color: var(--text-color);
        opacity: 0.7;
    }

</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 🎓 StudyMate")
    st.caption("Your AI Learning Companion")
    st.divider()

    st.markdown("### 📚 Study Tools")
    st.caption("Use the pages in the sidebar to access all features.")

    st.divider()
    st.caption(f"Version {APP_VERSION}")


# ---------------- DASHBOARD HEADER ----------------

st.markdown(f"""
<div class="hero">
    <h1>🎓 Welcome to {APP_NAME}</h1>
    <p>{APP_TAGLINE}</p>
    <p>Learn smarter. Prepare faster. Achieve more.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- FETCH DATA ----------------

study_history = get_study_history(limit=100)
quiz_results = get_quiz_results(limit=50)

total_activities = len(study_history)
total_quizzes = len(quiz_results)

if quiz_results:
    average_score = sum(
        row["score"] for row in quiz_results
    ) / len(quiz_results)
else:
    average_score = 0


# ---------------- DASHBOARD METRICS ----------------

st.markdown(
    '<div class="section-title">📊 Your Learning Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Study Activities",
        total_activities,
        help="Total saved study activities"
    )

with col2:
    st.metric(
        "Quizzes Attempted",
        total_quizzes
    )

with col3:
    st.metric(
        "Average Quiz Score",
        f"{average_score:.1f}%"
    )


# ---------------- FEATURES ----------------

st.markdown(
    '<div class="section-title">🚀 Explore Study Tools</div>',
    unsafe_allow_html=True
)

features = [
    ("💬 AI Study Chat", "Ask questions and understand difficult concepts."),
    ("📄 PDF Summarizer", "Convert lengthy PDFs into concise summaries."),
    ("🔍 Chat with PDF", "Ask questions directly from your documents."),
    ("📝 AI Notes Generator", "Create organized notes from any topic."),
    ("❓ MCQ Generator", "Generate multiple-choice practice questions."),
    ("🎯 Quiz Generator", "Test your knowledge with interactive quizzes."),
    ("✍️ Answer Evaluator", "Get AI feedback on your written answers."),
    ("📚 Study History", "Review your previous learning activities.")
]

for row_start in range(0, len(features), 4):

    columns = st.columns(4)

    for index, column in enumerate(columns):

        feature_index = row_start + index

        if feature_index >= len(features):
            break

        title, description = features[feature_index]

        with column:
            st.markdown(f"""
            <div class="feature-card">
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)


# ---------------- RECENT ACTIVITY ----------------

st.markdown(
    '<div class="section-title">🕒 Recent Study Activity</div>',
    unsafe_allow_html=True
)

if study_history:

    for activity in study_history[:5]:

        with st.container(border=True):

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{activity['title']}**")
                st.caption(activity["feature"])

                if activity["output_text"]:
                    st.write(
                        truncate_text(activity["output_text"], 180)
                    )

            with col2:
                st.caption(
                    format_timestamp(activity["created_at"])
                )

else:
    st.info(
        "No study activities yet. Start using the AI tools to build your learning history!"
    )


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    "<center class='footer-text'>"
    "Made with ❤️ using Python, Streamlit and Google Gemini"
    "</center>",
    unsafe_allow_html=True
)