"""
Configuration settings for the Streamlit AMA application.
"""
import os
from pathlib import Path

# Base directory for the application
BASE_DIR = Path(__file__).parent.parent

DB_PATH = os.path.join(BASE_DIR, "data", "auth.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploaded_files")

# Application settings
APP_TITLE = "AMA"
APP_ICON = "🤖"
APP_LAYOUT = "wide"
