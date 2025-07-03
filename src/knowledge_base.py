import json
from src import config

class KnowledgeBase:
    """
    Handles loading and accessing the user's personal data.
    Now with logic to dynamically create 'full_name'.
    """
    def __init__(self, profile_path=config.PROFILE_JSON_PATH):
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
        """
        Retrieves info from the knowledge base.
        Special case: Handles 'personal_info.full_name' dynamically.
        Special case: Handles list indices like 'work_experience.0.company'.
        """
        if not key_path:
            return None
            
        # --- NEW: DYNAMIC FULL NAME LOGIC ---
        if key_path == 'personal_info.full_name':
            first = self.get_info('personal_info.first_name')
            last = self.get_info('personal_info.last_name')
            if first and last:
                return f"{first} {last}"
            return None

        keys = key_path.split('.')
        value = self._data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                try:
                    index = int(key)
                    if 0 <= index < len(value):
                        value = value[index]
                    else:
                        return None 
                except (ValueError, TypeError):
                    return None
            else:
                return None
            
            if value is None:
                return None

        return value
