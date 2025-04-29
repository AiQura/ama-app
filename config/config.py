"""
Configuration settings for the Streamlit AMA application.
"""
import os
from pathlib import Path

# Base directory for the application
BASE_DIR = Path(__file__).parent.parent

UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploaded_files")

# Application settings
APP_TITLE = "AMA"
APP_ICON = "🤖"
APP_LAYOUT = "wide"

# AUTH Config
SESSION_DURATION_IN_DAYS = 1

CHROMA_PATH = os.path.join(BASE_DIR, ".chroma")
