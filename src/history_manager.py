# src/history_manager.py

import json
import os

HISTORY_FILE = 'answered_questions.json'

def load_history():
    """Loads the question and answer history from the JSON file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Return empty dict if file is corrupted or empty
    return {}

def save_history(history_data):
    """Saves the updated history to the JSON file."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history_data, f, indent=4)