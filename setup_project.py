import os

# --- Project Structure and Content Definition ---

# Define the directory structure
# os.path.join is used to make it compatible with any operating system
project_structure = {
    "data": None,
    "src": {
        "__init__.py": "",
        "ai_engine.py": "",
        "utils.py": ""
    }
}

# Define the content for each file
file_contents = {
    ".gitignore": """
# Python
__pycache__/
*.pyc

# Environment
.env

# Data Files
data/credentials.csv

# IDE / Editor specific
.vscode/
.idea/
""",

    "requirements.txt": """
python-dotenv
selenium
google-generativeai
webdriver-manager
""",

    ".env": """
# --- IntelliApply Bot Environment Variables ---

# Your API key for the Google Gemini AI
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
""",

    "data/profile.json": """
{
  "personal_info": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@email.com",
    "phone": "555-123-4567"
  },
  "technical_skills": {
    "python_years": 5,
    "selenium_expertise": "expert"
  }
}
""",

    "data/credentials.csv": "website,email,password\n",

    "src/config.py": """
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
""",

    "src/knowledge_base.py": """
import json
from src import config

class KnowledgeBase:
    \"\"\"
    Handles loading and accessing the user's personal data from the profile.json file.
    \"\"\"
    def __init__(self, profile_path=config.PROFILE_JSON_PATH):
        \"\"\"
        Initializes the KnowledgeBase and loads the profile data.
        \"\"\"
        try:
            with open(profile_path, 'r') as f:
                self._data = json.load(f)
            print("Knowledge Base loaded successfully.")
        except FileNotFoundError:
            print(f"Error: The profile file was not found at {profile_path}")
            self._data = {}
        except json.JSONDecodeError:
            print(f"Error: The profile file at {profile_path} is not a valid JSON.")
            self._data = {}

    def get_info(self, key_path):
        \"\"\"
        Retrieves a piece of information from the knowledge base using a dot-separated path.
        Example: get_info('personal_info.first_name') -> 'John'
        \"\"\"
        keys = key_path.split('.')
        value = self._data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None # Key not found
        return value
""",

    "src/browser_handler.py": """
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from src import config

class BrowserHandler:
    \"\"\"
    Manages all Selenium WebDriver interactions.
    \"\"\"
    def __init__(self):
        \"\"\"
        Initializes the Selenium WebDriver.
        \"\"\"
        options = webdriver.ChromeOptions()
        if config.HEADLESS_MODE:
            options.add_argument("--headless")
        
        # Using webdriver-manager to automatically handle the driver
        try:
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()), 
                options=options
            )
            self.driver.maximize_window()
            print("WebDriver initialized successfully.")
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            print("Please ensure Google Chrome is installed and you have a working internet connection.")
            self.driver = None


    def navigate_to_url(self, url):
        \"\"\"
        Navigates the browser to the specified URL.
        \"\"\"
        if self.driver:
            print(f"Navigating to: {url}")
            self.driver.get(url)

    def close_browser(self):
        \"\"\"
        Closes the WebDriver session.
        \"\"\"
        if self.driver:
            print("Closing the browser.")
            self.driver.quit()
""",

    "main.py": """
import time
import sys
from src.browser_handler import BrowserHandler
from src.knowledge_base import KnowledgeBase

def main():
    \"\"\"
    Main function to run the IntelliApply Bot.
    Phase 1: Foundation and Setup Test
    \"\"\"
    print("--- Starting IntelliApply Bot ---")
    
    # 1. Initialize the Knowledge Base
    kb = KnowledgeBase()
    first_name = kb.get_info('personal_info.first_name')
    if not first_name:
        print("Could not retrieve first name from Knowledge Base. Exiting.")
        sys.exit(1)
    print(f"Running for user: {first_name}")

    # 2. Initialize the Browser Handler
    browser = BrowserHandler()
    if not browser.driver:
        print("Browser handler failed to initialize. Exiting.")
        sys.exit(1)
    
    try:
        # 3. Navigate to a test URL
        test_url = "https://www.google.com" # We'll use a simple URL for testing
        browser.navigate_to_url(test_url)
        
        # Keep the browser open for a few seconds to verify it works
        print("Navigation successful. Browser will close in 10 seconds.")
        time.sleep(10)
        
    except Exception as e:
        print(f"An error occurred during browser navigation: {e}")
    finally:
        # 4. Ensure the browser is closed
        browser.close_browser()
        
    print("--- IntelliApply Bot finished. ---")


if __name__ == "__main__":
    main()
"""
}

def create_project_structure(base_path, structure):
    """Recursively creates directory structure."""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if content is None: # It's a directory
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")
        elif isinstance(content, dict): # It's a directory with sub-items
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")
            create_project_structure(path, content)

def create_project_files(base_path, files):
    """Creates files with their specified content."""
    for file_path, content in files.items():
        full_path = os.path.join(base_path, file_path)
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            # .strip() removes leading/trailing whitespace from our multiline strings
            f.write(content.strip())
        print(f"Created file:      {full_path}")


if __name__ == "__main__":
    print("--- Setting up IntelliApply_Bot Project ---")
    
    # The script should be run from within the IntelliApply_Bot folder
    current_directory = os.getcwd()
    
    create_project_structure(current_directory, project_structure)
    create_project_files(current_directory, file_contents)
    
    print("\n--- Project setup complete! ---")
    print("\nNext Steps:")
    print("1. Fill in your details in 'data/profile.json'.")
    print("2. Add your Gemini API key to the '.env' file.")
    print("3. Install required libraries by running: pip install -r requirements.txt")
    print("4. Run the main script to test Phase 1: python main.py")

