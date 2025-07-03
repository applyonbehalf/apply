import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Gemini API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- File Path Configurations ---
# The os.path.join ensures compatibility across different operating systems
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_JSON_PATH = os.path.join(BASE_DIR, 'data', 'profile.json')

# --- Browser/Selenium Configurations ---
# Set to True to run the browser in the background without a UI
HEADLESS_MODE = False