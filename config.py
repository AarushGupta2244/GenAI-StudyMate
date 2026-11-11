import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "GenAI StudyMate"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Your Personal AI-Powered Learning Assistant"

# Gemini API Key: Local .env or Streamlit Cloud Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-3.5-flash-lite"

DATABASE_PATH = os.path.join("data", "studymate.db")

MAX_FILE_SIZE_MB = 20
MAX_PDF_PAGES = 100
SUPPORTED_FILE_TYPES = ["pdf"]

DEFAULT_TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 4096

PRIMARY_COLOR = "#6366F1"
SECONDARY_COLOR = "#8B5CF6"
BACKGROUND_COLOR = "#0F172A"