# src/ai_engine.py (FIXED VERSION - Better Yes/No Handling)

import google.generativeai as genai
from src import config
import pypdf
import json
from datetime import datetime

class AIEngine:
    """Handles all interactions with the AI model, with intelligent context-aware matching and rule-based answering."""
    VERSION = "9.3"  # Fixed yes/no question handling

    def __init__(self):
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print(f"AIEngine Version: {self.VERSION} initialized successfully.")
        except Exception as e:
            print(f"Error initializing AI Engine: {e}")
            self.model = None

    def answer_yes_no_question(self, question_label, user_profile):
        """
        Enhanced Yes/No question answering with better keyword detection
        and profile-based reasoning.
        """
        question_lower = question_label.lower()
        
        # Enhanced sponsorship detection
        if any(keyword in question_lower for keyword in ["sponsorship", "visa", "sponsor"]):
            sponsorship_answer = user_profile.get("eligibility", {}).get("will_you_require_sponsorship", "No")
            print(f"AI: Sponsorship question detected. Answer from profile: {sponsorship_answer}")
            return sponsorship_answer
            
        # Work authorization detection
        if any(keyword in question_lower for keyword in ["authorized", "eligible", "work auth", "legally authorized"]):
            auth_answer = user_profile.get("eligibility", {}).get("are_you_legally_authorized_to_work", "Yes")
            print(f"AI: Work authorization question detected. Answer from profile: {auth_answer}")
            return auth_answer
            
        # Felony/conviction detection
        if any(keyword in question_lower for keyword in ["felony", "convicted", "criminal"]):
            felony_answer = user_profile.get("background", {}).get("have_you_ever_been_convicted_of_a_felony", "No")
            print(f"AI: Felony question detected. Answer from profile: {felony_answer}")
            return felony_answer
            
        # Background check consent
        if "background check" in question_lower:
            bg_answer = user_profile.get("background", {}).get("background_check_consent", "Yes")
            print(f"AI: Background check question detected. Answer from profile: {bg_answer}")
            return bg_answer
            
        # Certification/agreement questions
        if any(keyword in question_lower for keyword in ["certify", "agree", "accurate", "confirm"]):
            print("AI: Certification/agreement question detected. Answering: Yes")
            return "Yes"
            
        print(f"AI: No specific rule matched for question: {question_label}")
        return None

    def extract_work_history_from_resume(self, resume_path):
        if not self.model: return None
        print(f"AI: Reading resume from {resume_path}...")
        try:
            reader = pypdf.PdfReader(resume_path)
            resume_text = "".join(page.extract_text() or "" for page in reader.pages)
            if not resume_text:
                print("AI Error: Could not extract text from the resume PDF.")
                return None
        except Exception as e:
            print(f"AI Error: Failed to read or parse the resume PDF: {e}")
            return None
        
        prompt = f"""
        Analyze the following resume text and extract the work experience into a JSON object with a single key "work_experience".
        This should be a list of jobs, each with "job_title", "company", "start_date", "end_date", and "responsibilities".
        If an end date is not specified, use "Present". Format dates as YYYY-MM-DD.
        Resume Text: --- {resume_text} ---
        JSON Output:
        """
        print("AI: Asking AI to extract work history from resume...")
        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(json_text)
        except Exception as e:
            print(f"AI Error: Failed to generate or structured work history: {e}")
            return None

    def find_best_match_for_label(self, label_text, knowledge_base_keys):
        if not self.model: return None
        
        def normalize(text): return text.lower().replace("_", "").replace(" ", "")
        normalized_label = normalize(label_text)
        
        for key in knowledge_base_keys:
            if normalized_label in normalize(key) or normalize(key) in normalized_label:
                print(f"AIEngine: Direct match (fuzzy) for '{label_text}' -> '{key}'")
                return key
        
        keys_string = ", ".join(knowledge_base_keys)
        prompt = f"""
        You are an intelligent assistant mapping a web form label to a JSON key.
        The form label is: "{label_text}"
        Available JSON keys: [{keys_string}]
        Respond with ONLY the best matching key. If there is no logical match, respond with "None".
        Matching Key:
        """
        try:
            response = self.model.generate_content(prompt)
            best_key = response.text.strip()
            if best_key in knowledge_base_keys:
                print(f"AI intelligently matched '{label_text}' -> '{best_key}'")
                return best_key
            return None
        except Exception as e:
            print(f"AI error matching label: {e}")
            return None

    def infer_value_for_label(self, field_label, knowledge_base):
        if not self.model: return None
        profile_string = json.dumps(knowledge_base, indent=2)
        prompt = f"""
        Based on the following user profile (in JSON), return the most likely answer to the field label: '{field_label}'.
        Respond only with the appropriate answer in a single line (no explanation).
        User Profile: ```json\n{profile_string}\n```
        Answer:
        """
        print(f"AI: Trying to infer answer for missing field: '{field_label}'")
        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            print(f"AI response for '{field_label}': {answer}")
            return answer
        except Exception as e:
            print(f"AI error inferring value: {e}")
            return None

    def make_a_choice(self, question_label, options_list, user_profile):
        if not self.model: return None
        
        # First try rule-based answering for common questions
        rule_based_answer = self.answer_yes_no_question(question_label, user_profile)
        if rule_based_answer:
            # Find the matching option
            for option in options_list:
                if rule_based_answer.lower() in option.lower():
                    print(f"AI: Rule-based choice '{rule_based_answer}' matched to option '{option}'")
                    return option
        
        options_string = ", ".join(f"'{opt}'" for opt in options_list)
        profile_string = json.dumps(user_profile, indent=2)
        prompt = f"""
        You are an advanced AI assistant filling out a job application.
        The Question: "{question_label}"
        The Options: [{options_string}]
        The User's Full Profile: ```json\n{profile_string}\n```
        
        Your Task & Reasoning: Choose the single best option from the list based on the user's profile.
        Pay special attention to eligibility information, especially visa sponsorship requirements.
        
        Respond with ONLY the text of your final chosen option.
        Chosen Option:
        """
        try:
            print(f"AI is reasoning about the choice for: '{question_label}'")
            response = self.model.generate_content(prompt)
            best_option = response.text.strip().strip("'\"")
            
            for option in options_list:
                if best_option.lower() == option.lower():
                    print(f"AI reasoned and chose '{option}'")
                    return option
            
            for option in options_list:
                if best_option.lower() in option.lower() or option.lower() in best_option.lower():
                    print(f"AI reasoned and chose '{option}' (fuzzy match)")
                    return option
            
            print(f"AI could not match response '{best_option}' to any option")
            return None
        except Exception as e:
            print(f"AI error making a reasoned choice: {e}")
            return None
            
    def make_multiple_choices(self, question_label, options_list, user_profile):
        """Chooses one or more relevant options from a list for a multi-select question."""
        if not self.model: return []
        options_string = ", ".join(f"'{opt}'" for opt in options_list)
        profile_string = json.dumps(user_profile.get("preferences"), indent=2)
        prompt = f"""
        You are an AI assistant helping a user select all applicable options for a job application question.
        The Question: "{question_label}"
        The User's Preferences: ```json\n{profile_string}\n```
        All Available Options: [{options_string}]
        Your Task: Based on the user's preferences, identify ALL options from the list that are a good match.
        Respond with a Python-style list of strings of your chosen options. Example: ['Remote', 'Chicago']
        If no options are a good match, respond with an empty list: []
        Chosen Options List:
        """
        try:
            print(f"AI is reasoning about multiple choices for: '{question_label}'")
            response = self.model.generate_content(prompt)
            chosen_options = eval(response.text.strip())
            if isinstance(chosen_options, list):
                print(f"AI reasoned and chose multiple options: {chosen_options}")
                return chosen_options
            return []
        except Exception as e:
            print(f"AI error making multiple choices: {e}")
            return []

    def generate_essay_answer(self, question_label, user_essay_components):
        if not self.model: return None
        components_string = "\n".join([f"- {key}: {value}" for key, value in user_essay_components.items()]) if user_essay_components else "Not provided."
        prompt = f"""
        As a career coach, write a 2-3 sentence professional response to: "{question_label}"
        Use these points: {components_string}
        Your Response:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI error generating essay: {e}")
            return None