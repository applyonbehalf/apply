# bot/enhanced_ai_engine.py - Enhanced AI engine for multi-user applications
import google.generativeai as genai
from config import settings
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

class EnhancedAIEngine:
    """Enhanced AI engine with improved decision making and caching"""
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.field_mapping_cache = {}
            self.choice_cache = {}
            print("✅ Enhanced AI Engine initialized")
        except Exception as e:
            print(f"❌ AI Engine initialization error: {e}")
            self.model = None
    
    def map_field_to_profile_data(self, field_label: str, profile_data: Dict[str, Any]) -> Optional[str]:
        """Map a form field label to profile data using AI and caching"""
        
        # Create cache key
        cache_key = hashlib.md5(field_label.lower().encode()).hexdigest()
        
        # Check cache first
        if cache_key in self.field_mapping_cache:
            cached_result = self.field_mapping_cache[cache_key]
            print(f"🧠 Cache hit for field: {field_label} -> {cached_result}")
            return cached_result
        
        if not self.model:
            return self._fallback_field_mapping(field_label, profile_data)
        
        try:
            # Flatten profile data for AI analysis
            flattened_data = self._flatten_profile_data(profile_data)
            available_fields = list(flattened_data.keys())
            
            prompt = f"""
            You are an intelligent form-filling assistant. Given a form field label, find the best matching data field from the user's profile.
            
            Form Field Label: "{field_label}"
            
            Available Profile Fields: {available_fields[:20]}  # Limit for context
            
            Rules:
            1. Return the EXACT field name that best matches the form label
            2. If no good match exists, return "NONE"
            3. Consider common variations (e.g., "First Name" matches "legal_first_name")
            4. Consider context (e.g., "Phone" likely matches "phone" or "phone_number")
            
            Response format: Just the field name or "NONE"
            """
            
            response = self.model.generate_content(prompt)
            result = response.text.strip().replace('"', '').replace("'", "")
            
            # Validate result
            if result in available_fields:
                self.field_mapping_cache[cache_key] = result
                print(f"🧠 AI mapped: {field_label} -> {result}")
                return result
            elif result == "NONE":
                self.field_mapping_cache[cache_key] = None
                return None
            else:
                # Fallback to fuzzy matching
                fallback_result = self._fallback_field_mapping(field_label, profile_data)
                self.field_mapping_cache[cache_key] = fallback_result
                return fallback_result
                
        except Exception as e:
            print(f"❌ AI field mapping error: {e}")
            return self._fallback_field_mapping(field_label, profile_data)
    
    def _fallback_field_mapping(self, field_label: str, profile_data: Dict[str, Any]) -> Optional[str]:
        """Fallback field mapping using simple text matching"""
        flattened_data = self._flatten_profile_data(profile_data)
        field_lower = field_label.lower().replace(' ', '').replace('_', '')
        
        # Direct matches
        for key, value in flattened_data.items():
            key_lower = key.lower().replace(' ', '').replace('_', '')
            if field_lower in key_lower or key_lower in field_lower:
                return key
        
        # Common mappings
        mappings = {
            'firstname': ['legal_first_name', 'first_name', 'fname'],
            'lastname': ['legal_last_name', 'last_name', 'lname'], 
            'fullname': ['full_name', 'fullname', 'name'],
            'email': ['email', 'email_address'],
            'phone': ['phone', 'phone_number', 'mobile'],
            'address': ['address_line_1', 'address', 'street'],
            'city': ['city'],
            'state': ['state_province', 'state'],
            'zip': ['zip_postal_code', 'postal_code', 'zip'],
            'salary': ['salary_expectation', 'desired_salary'],
            'experience': ['total_years_professional_experience', 'years_experience']
        }
        
        for pattern, candidates in mappings.items():
            if pattern in field_lower:
                for candidate in candidates:
                    if candidate in flattened_data:
                        return candidate
        
        return None
    
    def _flatten_profile_data(self, profile_data: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested profile data"""
        flattened = {}
        
        for key, value in profile_data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_profile_data(value, new_key))
            else:
                flattened[new_key] = value
        
        return flattened
    
    def get_profile_value(self, field_path: str, profile_data: Dict[str, Any]) -> Optional[str]:
        """Get value from profile data using dot notation path"""
        try:
            keys = field_path.split('.')
            value = profile_data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            # Convert to string if not already
            if value is not None:
                if isinstance(value, list):
                    return ', '.join(str(item) for item in value)
                return str(value)
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting profile value: {e}")
            return None
    
    def make_intelligent_choice(self, question: str, options: List[str], profile_data: Dict[str, Any]) -> Optional[str]:
        """Make an intelligent choice using AI and caching"""
        
        # Create cache key
        cache_key = hashlib.md5(f"{question}:{','.join(options)}".encode()).hexdigest()
        
        # Check cache
        if cache_key in self.choice_cache:
            cached_choice = self.choice_cache[cache_key]
            print(f"🧠 Cache hit for choice: {question[:30]}... -> {cached_choice}")
            return cached_choice
        
        # Rule-based answers first
        rule_based_answer = self._rule_based_choice(question, options, profile_data)
        if rule_based_answer:
            self.choice_cache[cache_key] = rule_based_answer
            return rule_based_answer
        
        if not self.model:
            return self._fallback_choice(question, options, profile_data)
        
        try:
            # Prepare context from profile
            context = self._prepare_profile_context(profile_data)
            
            prompt = f"""
            You are helping someone fill out a job application form. Based on their profile, choose the best answer.
            
            Question: "{question}"
            Options: {options}
            
            User Profile Context:
            {context}
            
            Rules:
            1. Choose the option that best matches the user's profile
            2. Be conservative and professional
            3. If unsure, choose the safest/most common option
            4. Return ONLY the exact text of your chosen option
            
            Your choice:
            """
            
            response = self.model.generate_content(prompt)
            ai_choice = response.text.strip().replace('"', '').replace("'", "")
            
            # Validate choice is in options
            for option in options:
                if ai_choice.lower() == option.lower() or ai_choice in option or option in ai_choice:
                    self.choice_cache[cache_key] = option
                    print(f"🧠 AI chose: {question[:30]}... -> {option}")
                    return option
            
            # Fallback if AI choice doesn't match
            fallback_choice = self._fallback_choice(question, options, profile_data)
            self.choice_cache[cache_key] = fallback_choice
            return fallback_choice
            
        except Exception as e:
            print(f"❌ AI choice error: {e}")
            fallback_choice = self._fallback_choice(question, options, profile_data)
            self.choice_cache[cache_key] = fallback_choice
            return fallback_choice
    
    def _rule_based_choice(self, question: str, options: List[str], profile_data: Dict[str, Any]) -> Optional[str]:
        """Rule-based choice for common questions"""
        question_lower = question.lower()
        
        # Sponsorship questions
        if any(keyword in question_lower for keyword in ['sponsorship', 'visa', 'sponsor']):
            sponsorship_answer = self.get_profile_value('eligibility.will_you_require_sponsorship', profile_data)
            if sponsorship_answer:
                for option in options:
                    if sponsorship_answer.lower() in option.lower():
                        return option
        
        # Work authorization
        if any(keyword in question_lower for keyword in ['authorized', 'eligible', 'work auth']):
            auth_answer = self.get_profile_value('eligibility.are_you_legally_authorized_to_work', profile_data)
            if auth_answer:
                for option in options:
                    if auth_answer.lower() in option.lower():
                        return option
        
        # Work preference (remote/hybrid/onsite)
        if any(keyword in question_lower for keyword in ['remote', 'onsite', 'hybrid', 'work preference']):
            work_pref = self.get_profile_value('preferences.work_preference', profile_data)
            if work_pref:
                for option in options:
                    if work_pref.lower() in option.lower():
                        return option
        
        # Experience questions
        if 'experience' in question_lower and any(keyword in question_lower for keyword in ['years', 'how much', 'how long']):
            years_exp = self.get_profile_value('experience.total_years_professional_experience', profile_data)
            if years_exp:
                try:
                    years = int(years_exp)
                    for option in options:
                        option_lower = option.lower()
                        if years >= 5 and 'more than' in option_lower and ('3' in option_lower or '5' in option_lower):
                            return option
                        elif years >= 3 and '3' in option_lower and 'years' in option_lower:
                            return option
                        elif years >= 1 and '1' in option_lower and 'years' in option_lower:
                            return option
                        elif years == 0 and 'no experience' in option_lower:
                            return option
                except:
                    pass
        
        # Yes/No questions
        if '?' in question and len(options) == 2:
            yes_options = [opt for opt in options if opt.lower() in ['yes', 'y', 'true']]
            no_options = [opt for opt in options if opt.lower() in ['no', 'n', 'false']]
            
            if yes_options and no_options:
                # Default safe answers
                if any(keyword in question_lower for keyword in ['agree', 'certify', 'confirm', 'consent']):
                    return yes_options[0]
                elif any(keyword in question_lower for keyword in ['felony', 'convicted', 'criminal']):
                    return no_options[0]
        
        return None
    
    def _fallback_choice(self, question: str, options: List[str], profile_data: Dict[str, Any]) -> Optional[str]:
        """Simple fallback choice logic"""
        if not options:
            return None
        
        # For yes/no questions, be conservative
        if len(options) == 2:
            for option in options:
                if option.lower() in ['no', 'false', 'n']:
                    return option
        
        # Default to first option that's not obviously empty
        for option in options:
            if option.strip() and '--' not in option and 'select' not in option.lower():
                return option
        
        return options[0] if options else None
    
    def _prepare_profile_context(self, profile_data: Dict[str, Any]) -> str:
        """Prepare relevant profile context for AI"""
        try:
            context_parts = []
            
            # Personal info
            personal = profile_data.get('personal_info', {})
            if personal:
                context_parts.append(f"Name: {personal.get('legal_first_name', '')} {personal.get('legal_last_name', '')}")
                context_parts.append(f"Location: {personal.get('location', '')}")
            
            # Experience
            experience = profile_data.get('experience', {})
            if experience:
                context_parts.append(f"Experience: {experience.get('total_years_professional_experience', '')} years")
                context_parts.append(f"Salary expectation: {experience.get('salary_expectation', '')}")
            
            # Preferences
            preferences = profile_data.get('preferences', {})
            if preferences:
                context_parts.append(f"Work preference: {preferences.get('work_preference', '')}")
            
            # Eligibility
            eligibility = profile_data.get('eligibility', {})
            if eligibility:
                context_parts.append(f"Work authorized: {eligibility.get('are_you_legally_authorized_to_work', '')}")
                context_parts.append(f"Sponsorship needed: {eligibility.get('will_you_require_sponsorship', '')}")
            
            return '\n'.join([part for part in context_parts if part.split(': ', 1)[1]])
            
        except Exception as e:
            print(f"❌ Error preparing context: {e}")
            return "Profile context unavailable"
    
    def generate_essay_response(self, question: str, profile_data: Dict[str, Any], max_length: int = 500) -> str:
        """Generate essay response for textarea fields"""
        
        if not self.model:
            return self._fallback_essay_response(question, profile_data)
        
        try:
            context = self._prepare_profile_context(profile_data)
            
            prompt = f"""
            Write a professional, concise response to this job application question.
            
            Question: "{question}"
            
            Candidate Profile:
            {context}
            
            Requirements:
            1. Keep response under {max_length} characters
            2. Be professional and enthusiastic
            3. Use specific details from the profile when relevant
            4. Don't make up information not in the profile
            5. Focus on relevant experience and skills
            
            Response:
            """
            
            response = self.model.generate_content(prompt)
            essay = response.text.strip()
            
            # Ensure length limit
            if len(essay) > max_length:
                sentences = essay.split('. ')
                truncated = ''
                for sentence in sentences:
                    if len(truncated + sentence + '. ') <= max_length - 3:
                        truncated += sentence + '. '
                    else:
                        break
                essay = truncated.rstrip() + '...'
            
            print(f"📝 Generated essay response ({len(essay)} chars)")
            return essay
            
        except Exception as e:
            print(f"❌ Essay generation error: {e}")
            return self._fallback_essay_response(question, profile_data)
    
    def _fallback_essay_response(self, question: str, profile_data: Dict[str, Any]) -> str:
        """Fallback essay response"""
        try:
            # Get basic info
            personal = profile_data.get('personal_info', {})
            experience = profile_data.get('experience', {})
            
            name = personal.get('legal_first_name', 'I')
            years_exp = experience.get('total_years_professional_experience', 'several')
            
            # Generic but professional response
            if 'why' in question.lower() and 'interest' in question.lower():
                return f"I am very interested in this position because it aligns perfectly with my {years_exp} years of professional experience and career goals. I believe my skills and background make me a strong candidate for this role."
            
            elif 'tell' in question.lower() and 'about' in question.lower():
                return f"I am a dedicated professional with {years_exp} years of experience in my field. I am passionate about contributing to innovative projects and am excited about the opportunity to bring my skills to your team."
            
            else:
                return f"I have {years_exp} years of professional experience and am eager to contribute my skills and expertise to this role. I am committed to excellence and continuous learning."
                
        except Exception:
            return "I am excited about this opportunity and believe I would be a valuable addition to your team."
    
    def analyze_job_requirements(self, job_url: str, job_content: str = None) -> Dict[str, Any]:
        """Analyze job requirements (for future enhancements)"""
        # Placeholder for job analysis functionality
        return {
            'required_skills': [],
            'preferred_experience': None,
            'salary_range': None,
            'work_type': 'unknown'
        }
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get AI cache statistics"""
        return {
            'field_mappings_cached': len(self.field_mapping_cache),
            'choices_cached': len(self.choice_cache)
        }