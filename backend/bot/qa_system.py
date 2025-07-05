# bot/qa_system.py - NEW FILE: Hierarchical Q&A System Integration
import json
from typing import Dict, List, Optional, Any
from database.connection import db
from datetime import datetime
import hashlib
import re

class QASystem:
    """
    Hierarchical Q&A system that integrates with Supabase tables:
    - user_qa_cache: User-specific question/answer cache
    - site_field_patterns: Site-specific field patterns
    - application_qa_history: Historical Q&A for applications
    """
    
    def __init__(self):
        self.field_normalizations = {
            # Common field name normalizations
            'first name': ['firstname', 'fname', 'first_name', 'given_name'],
            'last name': ['lastname', 'lname', 'last_name', 'family_name', 'surname'],
            'full name': ['fullname', 'full_name', 'name', 'complete_name'],
            'email': ['email_address', 'email', 'e-mail', 'contact_email'],
            'phone': ['phone_number', 'mobile', 'telephone', 'contact_number'],
            'address': ['street_address', 'address_line_1', 'home_address'],
            'city': ['city', 'town', 'locality'],
            'state': ['state', 'province', 'region', 'state_province'],
            'zip': ['zip_code', 'postal_code', 'zip', 'postcode'],
            'salary': ['salary_expectation', 'expected_salary', 'compensation'],
            'experience': ['years_experience', 'work_experience', 'professional_experience'],
            'visa': ['visa_sponsorship', 'sponsorship', 'work_authorization'],
        }
        print("✅ Q&A System initialized")
    
    async def get_field_answer_hierarchical(self, 
                                          user_id: str, 
                                          application_id: str,
                                          field_label: str, 
                                          field_type: str,
                                          site_domain: str,
                                          profile_data: Dict[str, Any]) -> Optional[str]:
        """
        5-Level Hierarchical Data Lookup:
        1. User Profile Data (Direct mapping)
        2. User Q&A Cache (Personal learning)
        3. Site Field Patterns (Site-specific patterns)
        4. AI Analysis with Context
        5. Manual Input (Human intervention)
        """
        
        print(f"🔍 Hierarchical lookup for: {field_label} ({field_type})")
        
        # Normalize field label for better matching
        normalized_label = self._normalize_field_label(field_label)
        
        # LEVEL 1: USER PROFILE DATA (Primary Source)
        answer = await self._level1_profile_data(normalized_label, profile_data)
        if answer:
            print(f"✅ Level 1 (Profile): {field_label} → {answer}")
            await self._log_qa_history(application_id, user_id, field_label, answer, "profile_data")
            return answer
        
        # LEVEL 2: USER'S Q&A CACHE (Learning from past)
        answer = await self._level2_user_cache(user_id, normalized_label, site_domain)
        if answer:
            print(f"✅ Level 2 (Cache): {field_label} → {answer}")
            await self._log_qa_history(application_id, user_id, field_label, answer, "user_cache")
            # Update usage count
            await self._update_cache_usage(user_id, normalized_label, answer)
            return answer
        
        # LEVEL 3: SITE PATTERNS (Common answers for this site)
        answer = await self._level3_site_patterns(site_domain, normalized_label)
        if answer:
            print(f"✅ Level 3 (Site Pattern): {field_label} → {answer}")
            await self._log_qa_history(application_id, user_id, field_label, answer, "site_pattern")
            # Save to user cache for future use
            await self._save_to_user_cache(user_id, field_label, answer, site_domain, field_type, "site_pattern")
            return answer
        
        # LEVEL 4: AI ANALYSIS (Context-aware generation)
        answer = await self._level4_ai_analysis(user_id, field_label, field_type, profile_data, site_domain)
        if answer:
            print(f"✅ Level 4 (AI): {field_label} → {answer}")
            await self._log_qa_history(application_id, user_id, field_label, answer, "ai_generated")
            # Save to user cache
            await self._save_to_user_cache(user_id, field_label, answer, site_domain, field_type, "ai_generated")
            return answer
        
        # LEVEL 5: MANUAL INPUT (Human intervention)
        answer = await self._level5_manual_input(user_id, field_label, profile_data, site_domain, field_type)
        if answer:
            print(f"✅ Level 5 (Manual): {field_label} → {answer}")
            await self._log_qa_history(application_id, user_id, field_label, answer, "manual_input")
            # Save to user cache with high confidence
            await self._save_to_user_cache(user_id, field_label, answer, site_domain, field_type, "manual_input", confidence=1.0)
            return answer
        
        print(f"❌ No answer found for: {field_label}")
        return None
    
    def _normalize_field_label(self, field_label: str) -> str:
        """Normalize field label for better matching"""
        if not field_label:
            return ""
        
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', field_label.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    async def _level1_profile_data(self, field_label: str, profile_data: Dict[str, Any]) -> Optional[str]:
        """Level 1: Extract from user profile data"""
        
        # Flatten profile data for easier access
        flattened_data = self._flatten_profile_data(profile_data)
        
        # Direct field mappings
        field_mappings = {
            # Personal Information
            'first name': self._get_profile_value(['personal_info.legal_first_name', 'personal_info.first_name'], flattened_data),
            'last name': self._get_profile_value(['personal_info.legal_last_name', 'personal_info.last_name'], flattened_data),
            'full name': self._get_profile_value(['personal_info.full_name'], flattened_data),
            'email': self._get_profile_value(['personal_info.email'], flattened_data),
            'phone': self._get_profile_value(['personal_info.phone'], flattened_data),
            'address': self._get_profile_value(['personal_info.address_line_1', 'personal_info.address'], flattened_data),
            'city': self._get_profile_value(['personal_info.city'], flattened_data),
            'state': self._get_profile_value(['personal_info.state_province', 'personal_info.state'], flattened_data),
            'zip': self._get_profile_value(['personal_info.zip_postal_code', 'personal_info.postal_code'], flattened_data),
            
            # Experience & Career
            'salary': self._get_profile_value(['experience.salary_expectation'], flattened_data),
            'experience': self._get_profile_value(['experience.total_years_professional_experience'], flattened_data),
            'it experience': self._get_profile_value(['experience.it_managed_services_experience'], flattened_data),
            'security experience': self._get_profile_value(['experience.information_security_experience'], flattened_data),
            
            # Work Preferences
            'work preference': self._get_profile_value(['preferences.work_preference'], flattened_data),
            
            # Eligibility
            'visa sponsorship': self._get_profile_value(['eligibility.will_you_require_sponsorship', 'eligibility.visa_sponsorship'], flattened_data),
            'work authorization': self._get_profile_value(['eligibility.are_you_legally_authorized_to_work'], flattened_data),
        }
        
        # Check direct mappings first
        if field_label in field_mappings and field_mappings[field_label]:
            return str(field_mappings[field_label])
        
        # Check partial matches
        for pattern, value in field_mappings.items():
            if value and (pattern in field_label or field_label in pattern):
                return str(value)
        
        # Check normalizations
        for normalized_pattern, variants in self.field_normalizations.items():
            if normalized_pattern in field_label:
                if normalized_pattern in field_mappings and field_mappings[normalized_pattern]:
                    return str(field_mappings[normalized_pattern])
        
        return None
    
    def _get_profile_value(self, paths: List[str], flattened_data: Dict[str, Any]) -> Optional[str]:
        """Get value from flattened profile data using multiple possible paths"""
        for path in paths:
            if path in flattened_data and flattened_data[path]:
                return flattened_data[path]
        return None
    
    def _flatten_profile_data(self, profile_data: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested profile data for easier access"""
        flattened = {}
        
        for key, value in profile_data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                flattened.update(self._flatten_profile_data(value, new_key))
            else:
                flattened[new_key] = value
        
        return flattened
    
    async def _level2_user_cache(self, user_id: str, field_label: str, site_domain: str) -> Optional[str]:
        """Level 2: Check user's Q&A cache"""
        try:
            # Query user's cache with flexible matching
            response = await db.supabase.table('user_qa_cache').select('*').eq('user_id', user_id).execute()
            
            if not response.data:
                return None
            
            # Find best match
            best_match = None
            best_score = 0
            
            for cache_entry in response.data:
                cached_question = cache_entry['question_text'].lower()
                score = self._calculate_similarity(field_label, cached_question)
                
                # Boost score for same site
                if cache_entry.get('site_domain') == site_domain:
                    score += 0.2
                
                if score > best_score and score > 0.7:  # 70% similarity threshold
                    best_match = cache_entry
                    best_score = score
            
            return best_match['answer_text'] if best_match else None
            
        except Exception as e:
            print(f"❌ Error checking user cache: {e}")
            return None
    
    async def _level3_site_patterns(self, site_domain: str, field_label: str) -> Optional[str]:
        """Level 3: Check site-specific field patterns"""
        try:
            response = await db.supabase.table('site_field_patterns').select('*').eq('site_domain', site_domain).execute()
            
            if not response.data:
                return None
            
            # Find matching field pattern
            for pattern in response.data:
                pattern_label = pattern['field_label'].lower()
                if self._calculate_similarity(field_label, pattern_label) > 0.8:
                    # Get most common answer
                    common_answers = pattern.get('common_answers', {})
                    if isinstance(common_answers, dict) and common_answers:
                        # Return the most frequent answer
                        return max(common_answers, key=common_answers.get)
                    elif isinstance(common_answers, list) and common_answers:
                        return common_answers[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Error checking site patterns: {e}")
            return None
    
    async def _level4_ai_analysis(self, user_id: str, field_label: str, field_type: str, 
                                 profile_data: Dict[str, Any], site_domain: str) -> Optional[str]:
        """Level 4: AI analysis with full context"""
        try:
            # Import AI engine
            from bot.enhanced_ai_engine import EnhancedAIEngine
            ai_engine = EnhancedAIEngine()
            
            if not ai_engine.model:
                return self._fallback_ai_response(field_label, field_type, profile_data)
            
            # Prepare context
            context = self._prepare_ai_context(profile_data, site_domain)
            
            prompt = f"""
            You are helping someone fill out a job application form. Based on their profile, provide the best answer.
            
            Question: "{field_label}"
            Field Type: {field_type}
            Site: {site_domain}
            
            User Profile Context:
            {context}
            
            Rules:
            1. Use ONLY information from the user's profile
            2. Be concise and professional
            3. If the profile doesn't have the information, return "UNKNOWN"
            4. For yes/no questions, answer based on profile data
            5. Keep responses under 100 characters for form fields
            
            Answer:
            """
            
            response = ai_engine.model.generate_content(prompt)
            answer = response.text.strip()
            
            if answer and answer != "UNKNOWN" and len(answer) > 0:
                return answer
            
            return None
            
        except Exception as e:
            print(f"❌ Error in AI analysis: {e}")
            return self._fallback_ai_response(field_label, field_type, profile_data)
    
    def _fallback_ai_response(self, field_label: str, field_type: str, profile_data: Dict[str, Any]) -> Optional[str]:
        """Fallback AI response when Gemini is not available"""
        field_lower = field_label.lower()
        
        # Basic rule-based responses
        if any(word in field_lower for word in ['salary', 'compensation', 'pay']):
            salary = profile_data.get('experience', {}).get('salary_expectation')
            return salary if salary else "$80,000 - $100,000"
        
        elif any(word in field_lower for word in ['experience', 'years']):
            if 'security' in field_lower or 'cyber' in field_lower:
                return profile_data.get('experience', {}).get('information_security_experience', '2-3 years')
            elif 'it' in field_lower:
                return profile_data.get('experience', {}).get('it_managed_services_experience', '3-5 years')
            else:
                return profile_data.get('experience', {}).get('total_years_professional_experience', '3+ years')
        
        elif any(word in field_lower for word in ['visa', 'sponsorship']):
            return profile_data.get('eligibility', {}).get('will_you_require_sponsorship', 'No')
        
        elif any(word in field_lower for word in ['authorization', 'eligible']):
            return profile_data.get('eligibility', {}).get('are_you_legally_authorized_to_work', 'Yes')
        
        elif any(word in field_lower for word in ['remote', 'hybrid', 'preference']):
            return profile_data.get('preferences', {}).get('work_preference', 'Hybrid')
        
        return None
    
    def _prepare_ai_context(self, profile_data: Dict[str, Any], site_domain: str) -> str:
        """Prepare context for AI analysis"""
        context_parts = []
        
        # Personal info
        personal = profile_data.get('personal_info', {})
        if personal:
            context_parts.append(f"Name: {personal.get('full_name', 'N/A')}")
            context_parts.append(f"Email: {personal.get('email', 'N/A')}")
            context_parts.append(f"Location: {personal.get('city', 'N/A')}, {personal.get('state_province', 'N/A')}")
        
        # Experience
        experience = profile_data.get('experience', {})
        if experience:
            context_parts.append(f"Total Experience: {experience.get('total_years_professional_experience', 'N/A')}")
            context_parts.append(f"Salary Expectation: {experience.get('salary_expectation', 'N/A')}")
        
        # Eligibility
        eligibility = profile_data.get('eligibility', {})
        if eligibility:
            context_parts.append(f"Work Authorization: {eligibility.get('are_you_legally_authorized_to_work', 'N/A')}")
            context_parts.append(f"Visa Sponsorship: {eligibility.get('will_you_require_sponsorship', 'N/A')}")
        
        return '\n'.join([part for part in context_parts if 'N/A' not in part])
    
    async def _level5_manual_input(self, user_id: str, field_label: str, profile_data: Dict[str, Any], 
                                  site_domain: str, field_type: str) -> Optional[str]:
        """Level 5: Manual input (simulated for now, would be real UI in production)"""
        
        # For now, we'll return None to indicate manual input is needed
        # In a real implementation, this would:
        # 1. Create a manual input request in the database
        # 2. Send notification to user
        # 3. Wait for user response through web interface
        # 4. Return the user's answer
        
        print(f"🚨 MANUAL INPUT REQUIRED: {field_label}")
        print(f"   Site: {site_domain}")
        print(f"   Type: {field_type}")
        print(f"   User: {profile_data.get('personal_info', {}).get('full_name', 'Unknown')}")
        
        # For demo purposes, return a placeholder
        return "MANUAL_INPUT_REQUIRED"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        if text1 == text2:
            return 1.0
        
        # Simple word-based similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    async def _save_to_user_cache(self, user_id: str, question_text: str, answer_text: str,
                                 site_domain: str, field_type: str, source: str, confidence: float = 0.8):
        """Save answer to user's Q&A cache"""
        try:
            cache_data = {
                'user_id': user_id,
                'question_text': question_text,
                'answer_text': answer_text,
                'site_domain': site_domain,
                'field_type': field_type,
                'source': source,
                'confidence_score': confidence,
                'usage_count': 1
            }
            
            # Check if similar entry exists
            existing = await db.supabase.table('user_qa_cache').select('id').eq('user_id', user_id).eq('question_text', question_text).execute()
            
            if existing.data:
                # Update existing entry
                await db.supabase.table('user_qa_cache').update({
                    'answer_text': answer_text,
                    'confidence_score': confidence,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', existing.data[0]['id']).execute()
            else:
                # Create new entry
                await db.supabase.table('user_qa_cache').insert(cache_data).execute()
            
            print(f"💾 Saved to user cache: {question_text[:50]}... → {answer_text[:50]}...")
            
        except Exception as e:
            print(f"❌ Error saving to user cache: {e}")
    
    async def _update_cache_usage(self, user_id: str, question_text: str, answer_text: str):
        """Update usage count for cache entry"""
        try:
            await db.supabase.table('user_qa_cache').update({
                'usage_count': db.supabase.rpc('increment_usage_count'),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).eq('question_text', question_text).execute()
            
        except Exception as e:
            print(f"❌ Error updating cache usage: {e}")
    
    async def _log_qa_history(self, application_id: str, user_id: str, question_text: str, 
                             answer_text: str, answer_source: str):
        """Log Q&A to application history"""
        try:
            history_data = {
                'application_id': application_id,
                'user_id': user_id,
                'question_text': question_text,
                'answer_text': answer_text,
                'answer_source': answer_source,
                'processing_time_ms': 0  # Could track this if needed
            }
            
            await db.supabase.table('application_qa_history').insert(history_data).execute()
            
        except Exception as e:
            print(f"❌ Error logging Q&A history: {e}")
    
    async def update_site_patterns(self, site_domain: str, field_label: str, answer: str, field_type: str = None):
        """Update site-specific field patterns based on successful answers"""
        try:
            # Check if pattern exists
            existing = await db.supabase.table('site_field_patterns').select('*').eq('site_domain', site_domain).eq('field_label', field_label).execute()
            
            if existing.data:
                # Update existing pattern
                pattern = existing.data[0]
                common_answers = pattern.get('common_answers', {})
                
                if isinstance(common_answers, dict):
                    common_answers[answer] = common_answers.get(answer, 0) + 1
                else:
                    common_answers = {answer: 1}
                
                await db.supabase.table('site_field_patterns').update({
                    'common_answers': common_answers,
                    'usage_frequency': pattern.get('usage_frequency', 0) + 1
                }).eq('id', pattern['id']).execute()
            else:
                # Create new pattern
                pattern_data = {
                    'site_domain': site_domain,
                    'field_label': field_label,
                    'field_type': field_type,
                    'common_answers': {answer: 1},
                    'usage_frequency': 1
                }
                
                await db.supabase.table('site_field_patterns').insert(pattern_data).execute()
            
            print(f"📊 Updated site pattern: {site_domain} → {field_label}")
            
        except Exception as e:
            print(f"❌ Error updating site patterns: {e}")
    
    async def get_user_qa_stats(self, user_id: str) -> Dict[str, Any]:
        """Get Q&A statistics for a user"""
        try:
            # Count cache entries
            cache_response = await db.supabase.table('user_qa_cache').select('id', count='exact').eq('user_id', user_id).execute()
            cache_count = cache_response.count if hasattr(cache_response, 'count') else 0
            
            # Count recent Q&A history
            history_response = await db.supabase.table('application_qa_history').select('id', count='exact').eq('user_id', user_id).execute()
            history_count = history_response.count if hasattr(history_response, 'count') else 0
            
            return {
                'cached_questions': cache_count,
                'total_qa_interactions': history_count,
                'learning_enabled': True
            }
            
        except Exception as e:
            print(f"❌ Error getting Q&A stats: {e}")
            return {'cached_questions': 0, 'total_qa_interactions': 0, 'learning_enabled': False}