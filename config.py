import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application Configuration
APP_NAME = "GenAI StudyMate"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Your Personal AI-Powered Learning Assistant"

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.5-flash-lite"

# Database Configuration
DATABASE_PATH = os.path.join("data", "studymate.db")

# Upload Configuration
MAX_FILE_SIZE_MB = 20
MAX_PDF_PAGES = 100

# Application Settings
SUPPORTED_FILE_TYPES = ["pdf"]

# AI Settings
DEFAULT_TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 4096

# Theme Configuration
PRIMARY_COLOR = "#6366F1"
SECONDARY_COLOR = "#8B5CF6"
BACKGROUND_COLOR = "#0F172A"