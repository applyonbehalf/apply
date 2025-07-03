# database/connection.py - Fixed datetime handling
from supabase import create_client, Client
from config import settings
import asyncio
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, date
import uuid

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def prepare_data_for_supabase(data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare data for Supabase by converting datetime objects to strings"""
    if not isinstance(data, dict):
        return data
    
    prepared_data = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            prepared_data[key] = value.isoformat()
        elif isinstance(value, date):
            prepared_data[key] = value.isoformat()
        elif isinstance(value, dict):
            prepared_data[key] = prepare_data_for_supabase(value)
        elif isinstance(value, list):
            prepared_data[key] = [
                prepare_data_for_supabase(item) if isinstance(item, dict) else 
                item.isoformat() if isinstance(item, (datetime, date)) else item 
                for item in value
            ]
        else:
            prepared_data[key] = value
    
    return prepared_data

class DatabaseConnection:
    """Handles all database operations for IntelliApply with proper datetime handling"""
    
    def __init__(self):
        try:
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            print("✅ Database connection initialized")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            # Create a mock client for testing
            self.supabase = None
            self._mock_users = {}
            self._mock_profiles = {}
            self._mock_applications = {}
            self._mock_batches = {}
            self._mock_captcha_sessions = {}
            self._mock_notifications = {}
    
    def _is_mock_mode(self) -> bool:
        """Check if we're in mock mode"""
        return self.supabase is None
    
    # User operations
    async def create_user(self, user_data: dict) -> dict:
        """Create a new user with proper datetime handling"""
        try:
            if self._is_mock_mode():
                # Mock implementation
                prepared_data = prepare_data_for_supabase(user_data.copy())
                self._mock_users[prepared_data['email']] = prepared_data
                return prepared_data
            else:
                # Real Supabase implementation
                prepared_data = prepare_data_for_supabase(user_data.copy())
                
                # Remove fields that don't exist in the database schema
                db_fields = [
                    'id', 'email', 'name', 'password_hash', 'subscription_plan',
                    'applications_limit', 'applications_used', 'is_active', 'email_verified'
                ]
                
                # Only include fields that exist in the schema
                clean_data = {k: v for k, v in prepared_data.items() if k in db_fields}
                
                response = self.supabase.table('users').insert(clean_data).execute()
                return response.data[0] if response.data else None
                
        except Exception as e:
            print(f"Error creating user: {e}")
            # Fallback to mock mode
            prepared_data = prepare_data_for_supabase(user_data.copy())
            user_id = str(uuid.uuid4())
            mock_user = {
                'id': user_id,
                'email': prepared_data['email'],
                'name': prepared_data['name'],
                'password_hash': prepared_data['password_hash'],
                'subscription_plan': 'free',
                'applications_limit': 5,
                'applications_used': 0,
                'is_active': True,
                'email_verified': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            self._mock_users[prepared_data['email']] = mock_user
            return mock_user
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        try:
            if self._is_mock_mode():
                return self._mock_users.get(email)
            else:
                response = self.supabase.table('users').select('*').eq('email', email).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return self._mock_users.get(email) if hasattr(self, '_mock_users') else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        try:
            if self._is_mock_mode():
                for user in self._mock_users.values():
                    if user.get('id') == user_id:
                        return user
                return None
            else:
                response = self.supabase.table('users').select('*').eq('id', user_id).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            if hasattr(self, '_mock_users'):
                for user in self._mock_users.values():
                    if user.get('id') == user_id:
                        return user
            return None
    
    async def update_user(self, user_id: str, updates: dict) -> dict:
        """Update user data"""
        try:
            if self._is_mock_mode():
                for email, user in self._mock_users.items():
                    if user.get('id') == user_id:
                        prepared_updates = prepare_data_for_supabase(updates)
                        user.update(prepared_updates)
                        user['updated_at'] = datetime.utcnow().isoformat()
                        return user
                return None
            else:
                prepared_updates = prepare_data_for_supabase(updates)
                response = self.supabase.table('users').update(prepared_updates).eq('id', user_id).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    # Add these methods to your backend/database/connection.py file

    # Job Categories Operations
    async def get_job_categories(self) -> List[dict]:
        """Get all job categories"""
        try:
            if self._is_mock_mode():
                return [
                    {"id": "1", "category_name": "Cyber Security", "description": "Security roles"},
                    {"id": "2", "category_name": "Data Analyst", "description": "Data analysis roles"},
                    {"id": "3", "category_name": "Business Analyst", "description": "Business analysis roles"},
                    {"id": "4", "category_name": "Software Engineer", "description": "Software development roles"}
                ]
            else:
                response = self.supabase.table('job_categories').select('*').eq('is_active', True).execute()
                return response.data or []
        except Exception as e:
            print(f"Error getting job categories: {e}")
            return []

    async def create_job_category(self, category_data: dict) -> dict:
        """Create a new job category"""
        try:
            prepared_data = prepare_data_for_supabase(category_data.copy())
            
            if self._is_mock_mode():
                if not hasattr(self, '_mock_categories'):
                    self._mock_categories = {}
                self._mock_categories[prepared_data['id']] = prepared_data
                return prepared_data
            else:
                response = self.supabase.table('job_categories').insert(prepared_data).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating job category: {e}")
            return None

    async def get_job_category_by_id(self, category_id: str) -> Optional[dict]:
        """Get job category by ID"""
        try:
            if self._is_mock_mode():
                return getattr(self, '_mock_categories', {}).get(category_id)
            else:
                response = self.supabase.table('job_categories').select('*').eq('id', category_id).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting job category: {e}")
            return None

    # Job URLs Operations
    async def get_job_urls(self, category_id: str = None, status: str = None) -> List[dict]:
        """Get job URLs, optionally filtered"""
        try:
            if self._is_mock_mode():
                mock_urls = getattr(self, '_mock_job_urls', {})
                urls = list(mock_urls.values())
                
                if category_id:
                    urls = [url for url in urls if url.get('category_id') == category_id]
                if status:
                    urls = [url for url in urls if url.get('status') == status]
                
                return urls
            else:
                query = self.supabase.table('job_urls_master').select('*, job_categories(category_name)')
                
                if category_id:
                    query = query.eq('category_id', category_id)
                if status:
                    query = query.eq('status', status)
                
                response = query.execute()
                return response.data or []
        except Exception as e:
            print(f"Error getting job URLs: {e}")
            return []

    async def create_job_url(self, url_data: dict) -> dict:
        """Create a new job URL"""
        try:
            prepared_data = prepare_data_for_supabase(url_data.copy())
            
            if self._is_mock_mode():
                if not hasattr(self, '_mock_job_urls'):
                    self._mock_job_urls = {}
                self._mock_job_urls[prepared_data['id']] = prepared_data
                return prepared_data
            else:
                response = self.supabase.table('job_urls_master').insert(prepared_data).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating job URL: {e}")
            return None

    # User-Category Matching
    async def get_users_by_job_category(self, category_id: str) -> List[dict]:
        """Get users who are interested in a specific job category"""
        try:
            if self._is_mock_mode():
                # Mock: return some test users
                return [
                    {"user_id": "user1", "email": "user1@test.com", "category_id": category_id},
                    {"user_id": "user2", "email": "user2@test.com", "category_id": category_id}
                ]
            else:
                response = (
                    self.supabase.table('user_profiles')
                    .select('user_id, users(email, name)')
                    .eq('preferred_job_category_id', category_id)
                    .eq('is_active', True)
                    .execute()
                )
                return response.data or []
        except Exception as e:
            print(f"Error getting users by category: {e}")
            return []

    async def get_user_default_profile(self, user_id: str) -> Optional[dict]:
        """Get user's default profile"""
        try:
            if self._is_mock_mode():
                return {"id": f"profile_{user_id}", "user_id": user_id, "profile_name": "Default Profile"}
            else:
                response = (
                    self.supabase.table('user_profiles')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('is_default', True)
                    .eq('is_active', True)
                    .execute()
                )
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting default profile: {e}")
            return None

    # Admin Statistics
    async def get_admin_stats(self) -> dict:
        """Get statistics for admin dashboard"""
        try:
            if self._is_mock_mode():
                return {
                    "total_users": 10,
                    "total_categories": 4,
                    "total_job_urls": 50,
                    "active_applications": 25,
                    "completed_applications": 15,
                    "failed_applications": 5,
                    "pending_captchas": 2
                }
            else:
                # Get real statistics from database
                stats = {}
                
                # User count
                users_response = self.supabase.table('users').select('id', count='exact').execute()
                stats['total_users'] = users_response.count or 0
                
                # Categories count  
                categories_response = self.supabase.table('job_categories').select('id', count='exact').execute()
                stats['total_categories'] = categories_response.count or 0
                
                # Job URLs count
                urls_response = self.supabase.table('job_urls_master').select('id', count='exact').execute()
                stats['total_job_urls'] = urls_response.count or 0
                
                # Applications by status
                apps_response = self.supabase.table('job_applications').select('status').execute()
                applications = apps_response.data or []
                
                stats['active_applications'] = len([app for app in applications if app['status'] == 'queued'])
                stats['completed_applications'] = len([app for app in applications if app['status'] == 'completed'])
                stats['failed_applications'] = len([app for app in applications if app['status'] == 'failed'])
                stats['pending_captchas'] = len([app for app in applications if app['status'] == 'captcha_required'])
                
                return stats
                
        except Exception as e:
            print(f"Error getting admin stats: {e}")
            return {}

    async def get_all_users(self, category_id: str = None) -> List[dict]:
        """Get all users, optionally filtered by job category"""
        try:
            if self._is_mock_mode():
                return [
                    {"id": "user1", "email": "user1@test.com", "name": "User 1", "category": "Cyber Security"},
                    {"id": "user2", "email": "user2@test.com", "name": "User 2", "category": "Data Analyst"}
                ]
            else:
                if category_id:
                    response = (
                        self.supabase.table('users')
                        .select('*, user_profiles(profile_name, preferred_job_category_id, job_categories(category_name))')
                        .execute()
                    )
                    # Filter by category in Python since Supabase join filtering is complex
                    users = response.data or []
                    filtered_users = []
                    for user in users:
                        for profile in user.get('user_profiles', []):
                            if profile.get('preferred_job_category_id') == category_id:
                                filtered_users.append(user)
                                break
                    return filtered_users
                else:
                    response = (
                        self.supabase.table('users')
                        .select('*, user_profiles(profile_name, job_categories(category_name))')
                        .execute()
                    )
                    return response.data or []
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []


    # User Profile operations with mock fallbacks
    async def create_profile(self, profile_data: dict) -> dict:
        """Create a new user profile"""
        try:
            if self._is_mock_mode():
                prepared_data = prepare_data_for_supabase(profile_data.copy())
                self._mock_profiles[prepared_data['id']] = prepared_data
                return prepared_data
            else:
                prepared_data = prepare_data_for_supabase(profile_data.copy())
                response = self.supabase.table('user_profiles').insert(prepared_data).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating profile: {e}")
            # Fallback to mock
            prepared_data = prepare_data_for_supabase(profile_data.copy())
            if not hasattr(self, '_mock_profiles'):
                self._mock_profiles = {}
            self._mock_profiles[prepared_data['id']] = prepared_data
            return prepared_data
    
    async def get_user_profiles(self, user_id: str) -> List[dict]:
        """Get all profiles for a user"""
        try:
            if self._is_mock_mode():
                return [p for p in self._mock_profiles.values() if p.get('user_id') == user_id]
            else:
                response = self.supabase.table('user_profiles').select('*').eq('user_id', user_id).eq('is_active', True).execute()
                return response.data or []
        except Exception as e:
            print(f"Error getting user profiles: {e}")
            if hasattr(self, '_mock_profiles'):
                return [p for p in self._mock_profiles.values() if p.get('user_id') == user_id]
            return []
    
    async def get_profile_by_id(self, profile_id: str) -> Optional[dict]:
        """Get profile by ID"""
        try:
            if self._is_mock_mode():
                return self._mock_profiles.get(profile_id)
            else:
                response = self.supabase.table('user_profiles').select('*').eq('id', profile_id).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting profile by ID: {e}")
            if hasattr(self, '_mock_profiles'):
                return self._mock_profiles.get(profile_id)
            return None
    
    # Application operations with mock fallbacks
    async def create_application(self, app_data: dict) -> dict:
        """Create a new job application"""
        try:
            if self._is_mock_mode():
                prepared_data = prepare_data_for_supabase(app_data.copy())
                self._mock_applications[prepared_data['id']] = prepared_data
                return prepared_data
            else:
                prepared_data = prepare_data_for_supabase(app_data.copy())
                response = self.supabase.table('job_applications').insert(prepared_data).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating application: {e}")
            # Fallback to mock
            prepared_data = prepare_data_for_supabase(app_data.copy())
            if not hasattr(self, '_mock_applications'):
                self._mock_applications = {}
            self._mock_applications[prepared_data['id']] = prepared_data
            return prepared_data
    
    async def get_user_applications(self, user_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get applications for a user"""
        try:
            if self._is_mock_mode():
                user_apps = [app for app in self._mock_applications.values() if app.get('user_id') == user_id]
                return user_apps[offset:offset + limit]
            else:
                response = (
                    self.supabase.table('job_applications')
                    .select('*')
                    .eq('user_id', user_id)
                    .order('created_at', desc=True)
                    .range(offset, offset + limit - 1)
                    .execute()
                )
                return response.data or []
        except Exception as e:
            print(f"Error getting user applications: {e}")
            if hasattr(self, '_mock_applications'):
                user_apps = [app for app in self._mock_applications.values() if app.get('user_id') == user_id]
                return user_apps[offset:offset + limit]
            return []
    
    # Statistics with mock fallbacks
    async def get_user_stats(self, user_id: str) -> dict:
        """Get user application statistics"""
        try:
            if self._is_mock_mode():
                user_apps = [app for app in self._mock_applications.values() if app.get('user_id') == user_id]
            else:
                apps_response = (
                    self.supabase.table('job_applications')
                    .select('status')
                    .eq('user_id', user_id)
                    .execute()
                )
                user_apps = apps_response.data or []
            
            stats = {
                'total_applications': len(user_apps),
                'queued': len([app for app in user_apps if app.get('status') == 'queued']),
                'processing': len([app for app in user_apps if app.get('status') == 'processing']),
                'completed': len([app for app in user_apps if app.get('status') == 'completed']),
                'failed': len([app for app in user_apps if app.get('status') == 'failed']),
                'captcha_required': len([app for app in user_apps if app.get('status') == 'captcha_required'])
            }
            
            # Calculate success rate
            if stats['total_applications'] > 0:
                stats['success_rate'] = (stats['completed'] / stats['total_applications']) * 100
            else:
                stats['success_rate'] = 0
            
            return stats
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                'total_applications': 0,
                'queued': 0,
                'processing': 0,
                'completed': 0,
                'failed': 0,
                'captcha_required': 0,
                'success_rate': 0
            }
    
    # Add placeholder methods for other operations
    async def create_batch(self, batch_data: dict) -> dict:
        """Create a new application batch"""
        try:
            prepared_data = prepare_data_for_supabase(batch_data.copy())
            if self._is_mock_mode():
                if not hasattr(self, '_mock_batches'):
                    self._mock_batches = {}
                self._mock_batches[prepared_data['id']] = prepared_data
                return prepared_data
            else:
                response = self.supabase.table('application_batches').insert(prepared_data).execute()
                return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating batch: {e}")
            return prepared_data
    
    async def get_user_batches(self, user_id: str) -> List[dict]:
        """Get all batches for a user"""
        try:
            if self._is_mock_mode():
                if not hasattr(self, '_mock_batches'):
                    self._mock_batches = {}
                return [b for b in self._mock_batches.values() if b.get('user_id') == user_id]
            else:
                response = (
                    self.supabase.table('application_batches')
                    .select('*')
                    .eq('user_id', user_id)
                    .order('created_at', desc=True)
                    .execute()
                )
                return response.data or []
        except Exception as e:
            print(f"Error getting user batches: {e}")
            return []
    
    async def get_pending_captchas(self) -> List[dict]:
        """Get all pending CAPTCHA sessions"""
        try:
            if self._is_mock_mode():
                if not hasattr(self, '_mock_captcha_sessions'):
                    self._mock_captcha_sessions = {}
                return [s for s in self._mock_captcha_sessions.values() if s.get('status') == 'pending']
            else:
                response = (
                    self.supabase.table('captcha_sessions')
                    .select('*, job_applications(job_title, company_name, user_id)')
                    .eq('status', 'pending')
                    .order('created_at', desc=False)
                    .execute()
                )
                return response.data or []
        except Exception as e:
            print(f"Error getting pending captchas: {e}")
            return []

# Create global database instance
db = DatabaseConnection()