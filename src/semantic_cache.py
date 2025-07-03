# src/semantic_cache.py (FIXED VERSION)
import json
import os
from src import config

# Define the path for our cache file
CACHE_FILE_PATH = os.path.join(config.BASE_DIR, 'data', 'semantic_cache.json')

def load_cache():
    """
    Loads the semantic cache from the JSON file.
    The new format separates field mappings from choice mappings.
    It automatically handles migrating old cache files to the new format.
    """
    if not os.path.exists(CACHE_FILE_PATH):
        # Return the new, structured format if no file exists
        return {"field_mappings": {}, "choice_mappings": {}}

    try:
        with open(CACHE_FILE_PATH, 'r') as f:
            data = json.load(f)
            # Check if it's the old format (flat structure)
            if not isinstance(data.get("field_mappings"), dict) or not isinstance(data.get("choice_mappings"), dict):
                print("CACHE: Old cache format detected. Migrating to new format.")
                # Assume all old keys are field mappings
                return {"field_mappings": data, "choice_mappings": {}}
            return data
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or unreadable, start fresh
        return {"field_mappings": {}, "choice_mappings": {}}

def save_cache(cache_data):
    """
    Saves the structured cache data to the JSON file.
    """
    try:
        with open(CACHE_FILE_PATH, 'w') as f:
            json.dump(cache_data, f, indent=4)
    except IOError as e:
        print(f"Error: Could not write to cache file at {CACHE_FILE_PATH}: {e}")

# --- Functions for Field Mappings (Label -> KB Key) ---

def get_field_mapping(label):
    """Retrieves a mapped knowledge base key for a given label."""
    cache_data = load_cache()
    return cache_data.get("field_mappings", {}).get(label)

def add_field_mapping(label, key):
    """Adds a new label-to-key mapping to the cache."""
    print(f"CACHE: Learning new FIELD mapping: '{label}' -> '{key}'")
    cache_data = load_cache()
    if "field_mappings" not in cache_data:
        cache_data["field_mappings"] = {}
    cache_data["field_mappings"][label] = key
    save_cache(cache_data)

# --- Functions for Choice Mappings (Question -> Answer) ---

def get_choice_mapping(question_label):
    """Retrieves a saved choice for a given question label."""
    cache_data = load_cache()
    return cache_data.get("choice_mappings", {}).get(question_label)

def add_choice_mapping(question_label, choice):
    """Adds a new question-to-choice mapping to the cache."""
    print(f"CACHE: Learning new CHOICE mapping: '{question_label}' -> '{choice}'")
    cache_data = load_cache()
    if "choice_mappings" not in cache_data:
        cache_data["choice_mappings"] = {}
    cache_data["choice_mappings"][question_label] = choice
    save_cache(cache_data)