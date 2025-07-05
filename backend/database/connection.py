# database/connection.py - Complete version with all methods
from supabase import create_client, Client
from config import settings
import asyncio
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class DatabaseConnection:
    """Handles all database operations for IntelliApply"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
    
    # User operations
    async def create_user(self, user_data: dict) -> dict:
        """Create a new user"""
        response = self.supabase.table('users').insert(user_data).execute()
        return response.data[0] if response.data else None
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        response = self.supabase.table('users').select('*').eq('email', email).execute()
        return response.data[0] if response.data else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        response = self.supabase.table('users').select('*').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    async def update_user(self, user_id: str, updates: dict) -> dict:
        """Update user data"""
        response = self.supabase.table('users').update(updates).eq('id', user_id).execute()
        return response.data[0] if response.data else None
    
    # User Profile operations
    async def create_profile(self, profile_data: dict) -> dict:
        """Create a new user profile"""
        response = self.supabase.table('user_profiles').insert(profile_data).execute()
        return response.data[0] if response.data else None
    
    async def get_user_profiles(self, user_id: str) -> List[dict]:
        """Get all profiles for a user"""
        response = self.supabase.table('user_profiles').select('*').eq('user_id', user_id).eq('is_active', True).execute()
        return response.data or []
    
    async def get_profile_by_id(self, profile_id: str) -> Optional[dict]:
        """Get profile by ID"""
        response = self.supabase.table('user_profiles').select('*').eq('id', profile_id).execute()
        return response.data[0] if response.data else None
    
    async def update_profile(self, profile_id: str, updates: dict) -> dict:
        """Update profile data"""
        response = self.supabase.table('user_profiles').update(updates).eq('id', profile_id).execute()
        return response.data[0] if response.data else None
    
    async def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile (soft delete)"""
        response = self.supabase.table('user_profiles').update({'is_active': False}).eq('id', profile_id).execute()
        return len(response.data) > 0
    
    # Job Application operations
    async def create_application(self, app_data: dict) -> dict:
        """Create a new job application"""
        response = self.supabase.table('job_applications').insert(app_data).execute()
        return response.data[0] if response.data else None
    
    async def get_user_applications(self, user_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get applications for a user"""
        response = (
            self.supabase.table('job_applications')
            .select('*')
            .eq('user_id', user_id)
            .order('created_at', desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return response.data or []
    
    async def get_next_queued_application(self) -> Optional[dict]:
        """Get the next application to process"""
        try:
            response = self.supabase.rpc('get_next_queued_application').execute()
            return response.data[0] if response.data else None
        except:
            # Fallback if RPC doesn't exist
            response = (
                self.supabase.table('job_applications')
                .select('*')
                .eq('status', 'queued')
                .order('priority', desc=True)
                .order('created_at', desc=False)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
    
    async def update_application_status(self, app_id: str, status: str, error_message: str = None) -> bool:
        """Update application status"""
        try:
            updates = {'status': status, 'updated_at': datetime.utcnow().isoformat()}
            if error_message:
                updates['error_message'] = error_message
            
            self.supabase.table('job_applications').update(updates).eq('id', app_id).execute()
            return True
        except Exception as e:
            print(f"Error updating application status: {e}")
            return False

    async def get_application_by_id(self, app_id: str) -> Optional[dict]:
        """Get application by ID"""
        response = self.supabase.table('job_applications').select('*').eq('id', app_id).execute()
        return response.data[0] if response.data else None

    async def get_applications_by_status(self, status: str, limit: int = 10) -> List[dict]:
        """Get applications by status"""
        try:
            response = (
                self.supabase.table('job_applications')
                .select('*')
                .eq('status', status)
                .order('priority', desc=True)
                .order('created_at', desc=False)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            print(f"Error getting applications by status: {e}")
            return []
    
    # Batch operations
    async def create_batch(self, batch_data: dict) -> dict:
        """Create a new application batch"""
        response = self.supabase.table('application_batches').insert(batch_data).execute()
        return response.data[0] if response.data else None
    
    async def get_user_batches(self, user_id: str) -> List[dict]:
        """Get all batches for a user"""
        response = (
            self.supabase.table('application_batches')
            .select('*')
            .eq('user_id', user_id)
            .order('created_at', desc=True)
            .execute()
        )
        return response.data or []

    async def get_batch_by_id(self, batch_id: str) -> Optional[dict]:
        """Get batch by ID"""
        response = self.supabase.table('application_batches').select('*').eq('id', batch_id).execute()
        return response.data[0] if response.data else None
    
    async def update_batch_progress(self, batch_id: str, processed_count: int, successful_count: int, failed_count: int) -> bool:
        """Update batch progress"""
        try:
            updates = {
                'processed_count': processed_count,
                'successful_count': successful_count,
                'failed_count': failed_count,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('application_batches').update(updates).eq('id', batch_id).execute()
            return True
        except Exception as e:
            print(f"Error updating batch progress: {e}")
            return False
    
    # CAPTCHA operations
    async def create_captcha_session(self, session_data: dict) -> dict:
        """Create a new CAPTCHA session"""
        response = self.supabase.table('captcha_sessions').insert(session_data).execute()
        return response.data[0] if response.data else None
    
    async def get_pending_captchas(self) -> List[dict]:
        """Get all pending CAPTCHA sessions"""
        response = (
            self.supabase.table('captcha_sessions')
            .select('*')
            .eq('status', 'pending')
            .order('created_at', desc=False)
            .execute()
        )
        return response.data or []

    async def get_captcha_session(self, session_id: str) -> Optional[dict]:
        """Get CAPTCHA session by ID"""
        response = self.supabase.table('captcha_sessions').select('*').eq('id', session_id).execute()
        return response.data[0] if response.data else None
    
    async def update_captcha_status(self, session_id: str, status: str, solved_by: str = None) -> bool:
        """Update CAPTCHA session status"""
        try:
            updates = {'status': status}
            if status == 'solved' and solved_by:
                updates['solved_at'] = datetime.utcnow().isoformat()
                updates['solved_by'] = solved_by
            
            self.supabase.table('captcha_sessions').update(updates).eq('id', session_id).execute()
            return True
        except Exception as e:
            print(f"Error updating CAPTCHA status: {e}")
            return False
    
    # Notification operations
    async def create_notification(self, notification_data: dict) -> dict:
        """Create a new notification"""
        try:
            response = self.supabase.table('notifications').insert(notification_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None
    
    async def get_user_notifications(self, user_id: str, unread_only: bool = False) -> List[dict]:
        """Get notifications for a user"""
        try:
            query = self.supabase.table('notifications').select('*').eq('user_id', user_id)
            
            if unread_only:
                query = query.eq('is_read', False)
            
            response = query.order('created_at', desc=True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting user notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        try:
            self.supabase.table('notifications').update({'is_read': True}).eq('id', notification_id).execute()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False

    async def pause_user_applications(self, user_id: str) -> int:
        """Pause all queued applications for a user"""
        try:
            response = (
                self.supabase.table('job_applications')
                .update({'status': 'paused'})
                .eq('user_id', user_id)
                .eq('status', 'queued')
                .execute()
            )
            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"Error pausing applications: {e}")
            return 0

    async def resume_user_applications(self, user_id: str) -> int:
        """Resume all paused applications for a user"""
        try:
            response = (
                self.supabase.table('job_applications')
                .update({'status': 'queued'})
                .eq('user_id', user_id)
                .eq('status', 'paused')
                .execute()
            )
            return len(response.data) if response.data else 0
        except Exception as e:
            print(f"Error resuming applications: {e}")
            return 0

    async def get_job_urls(self, category_id: str = None, status: str = None):
        """Get job URLs, optionally filtered"""
        try:
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

    # Add these methods to your backend/database/connection.py file
# Add at the end of your DatabaseConnection class

    async def get_job_categories(self):
        """Get all job categories"""
        try:
            response = self.supabase.table('job_categories').select('*').eq('is_active', True).execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting job categories: {e}")
            return []
    
    async def create_job_category(self, category_data: dict):
        """Create a new job category"""
        try:
            response = self.supabase.table('job_categories').insert(category_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating job category: {e}")
            return None
    
    async def get_job_category_by_id(self, category_id: str):
        """Get job category by ID"""
        try:
            response = self.supabase.table('job_categories').select('*').eq('id', category_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting job category: {e}")
            return None
    
    async def get_job_urls(self, category_id: str = None, status: str = None):
        """Get job URLs, optionally filtered"""
        try:
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
    
    async def create_job_url(self, url_data: dict):
        """Create a new job URL"""
        try:
            response = self.supabase.table('job_urls_master').insert(url_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating job URL: {e}")
            return None
    
    async def get_users_by_job_category(self, category_id: str) -> List[dict]:
        """Get users who are interested in a specific job category"""
        try:
            print(f'🔍 Looking for users with category: {category_id}')

            # Step 1: Get user profiles with the category preference
            profiles_response = (
                self.supabase.table('user_profiles')
                .select('user_id, id, profile_name')
                .eq('preferred_job_category_id', category_id)
                .eq('is_active', True)
                .execute()
            )

            print(f'📋 Found {len(profiles_response.data)} profiles with category preference')

            if not profiles_response.data:
                print('⚠️ No profiles found with this category preference')
                return []

            # Step 2: Get user details for each profile
            users = []
            for profile in profiles_response.data:
                user_id = profile['user_id']
                profile_id = profile['id']
                profile_name = profile['profile_name']

                # Get user details
                user_response = (
                    self.supabase.table('users')
                    .select('email, name')
                    .eq('id', user_id)
                    .execute()
                )

                if user_response.data:
                    user_data = user_response.data[0]
                    users.append({
                        'user_id': user_id,
                        'email': user_data['email'],
                        'name': user_data.get('name', ''),
                        'profile_id': profile_id,
                        'profile_name': profile_name
                    })
                    print(f'   ✅ Added user: {user_data["email"]}')

            print(f'🎯 Returning {len(users)} users')
            return users

        except Exception as e:
            print(f'❌ Error getting users by category: {e}')
            import traceback
            traceback.print_exc()
            return []
            # Direct table query that we know works from debug output
            response = (
                self.supabase.table('user_profiles')
                .select('user_id, id AS profile_id, profile_name, users(email, name)')
                .eq('preferred_job_category_id', category_id)
                .eq('is_active', True)
                .execute()
            )
            
            print(f"📋 Raw query returned {len(response.data)} profiles")
            
            users = []
            for profile in response.data or []:
                user_data = profile.get('users')
                if user_data:
                    users.append({
                        'user_id': profile['user_id'],
                        'email': user_data['email'],
                        'name': user_data.get('name', ''),
                        'profile_id': profile['profile_id'],
                        'profile_name': profile['profile_name']
                    })
                    print(f"   ✅ Added user: {user_data['email']}")
            
            print(f"🎯 Returning {len(users)} users")
            return users
            
        except Exception as e:
            print(f"❌ Error getting users by category: {e}")
            import traceback
            traceback.print_exc()
            return []
    async def get_user_default_profile(self, user_id: str):
        """Get user's default profile"""
        try:
            response = (
                self.supabase.table('user_profiles')
                .select('*')
                .eq('user_id', user_id)
                .eq('is_active', True)
                .order('is_default', desc=True)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting default profile: {e}")
            return None
    
    async def get_admin_stats(self):
        """Get admin dashboard statistics"""
        try:
            # Call the database function we created
            response = self.supabase.rpc('get_admin_dashboard_stats').execute()
            return response.data or {}
        except Exception as e:
            print(f"Error getting admin stats: {e}")
            # Fallback to manual calculation
            try:
                stats = {}
                
                users_response = self.supabase.table('users').select('id', count='exact').execute()
                stats['total_users'] = users_response.count or 0
                
                categories_response = self.supabase.table('job_categories').select('id', count='exact').execute()
                stats['total_categories'] = categories_response.count or 0
                
                urls_response = self.supabase.table('job_urls_master').select('id', count='exact').execute()
                stats['total_job_urls'] = urls_response.count or 0
                
                # Get application counts by status
                apps_response = self.supabase.table('job_applications').select('status').execute()
                applications = apps_response.data or []
                
                stats['active_applications'] = len([app for app in applications if app['status'] in ['queued', 'processing']])
                stats['completed_applications'] = len([app for app in applications if app['status'] == 'completed'])
                stats['failed_applications'] = len([app for app in applications if app['status'] == 'failed'])
                stats['pending_captchas'] = len([app for app in applications if app['status'] == 'captcha_required'])
                
                return stats
            except Exception as fallback_error:
                print(f"Fallback stats calculation failed: {fallback_error}")
                return {}
    
    async def create_application(self, app_data: dict):
        """Create a new job application"""
        try:
            response = self.supabase.table('job_applications').insert(app_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating application: {e}")
            return None
    
    async def execute(self, query: str, params: tuple = None):
        """Execute a raw SQL query (simplified version)"""
        try:
            # For now, we'll implement common operations
            if "UPDATE users SET applications_used" in query:
                user_id = params[0] if params else None
                if user_id:
                    response = self.supabase.table('users').update({
                        'applications_used': 'applications_used + 1'
                    }).eq('id', user_id).execute()
                    return response.data
            
            # Add more query patterns as needed
            print(f"Raw query not implemented: {query}")
            return None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    async def fetch_all(self, query: str, params: tuple = None):
        """Fetch all results from a query"""
        try:
            # Implement common fetch patterns
            if "SELECT" in query and "job_applications" in query:
                response = self.supabase.table('job_applications').select('*').execute()
                return response.data or []
            
            print(f"Fetch query not implemented: {query}")
            return []
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
    
    async def fetch_one(self, query: str, params: tuple = None):
        """Fetch one result from a query"""
        try:
            results = await self.fetch_all(query, params)
            return results[0] if results else None
        except Exception as e:
            print(f"Error fetching one: {e}")
            return None

    # Analytics operations
    async def get_user_stats(self, user_id: str) -> dict:
        """Get user application statistics"""
        # Get application counts by status
        apps_response = (
            self.supabase.table('job_applications')
            .select('status')
            .eq('user_id', user_id)
            .execute()
        )
        
        applications = apps_response.data or []
        
        stats = {
            'total_applications': len(applications),
            'queued': len([app for app in applications if app['status'] == 'queued']),
            'processing': len([app for app in applications if app['status'] == 'processing']),
            'completed': len([app for app in applications if app['status'] == 'completed']),
            'failed': len([app for app in applications if app['status'] == 'failed']),
            'captcha_required': len([app for app in applications if app['status'] == 'captcha_required'])
        }
        
        # Calculate success rate
        if stats['total_applications'] > 0:
            stats['success_rate'] = (stats['completed'] / stats['total_applications']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats

# Create global database instance
    async def get_all_users(self, category_id: Optional[str] = None) -> List[dict]:
        """Get all users, optionally filtered by job category preference"""
        try:
            if category_id:
                print(f"🔍 Getting users for category: {category_id}")
                
                # Use the fixed get_users_by_job_category function
                users_with_category = await self.get_users_by_job_category(category_id)
                
                # Convert to the format expected by the API
                result = []
                seen_users = set()
                
                for user in users_with_category:
                    user_id = user['user_id']
                    if user_id not in seen_users:
                        result.append({
                            'id': user_id,
                            'email': user['email'],
                            'name': user.get('name', ''),
                            'subscription_plan': 'free'  # Default value
                        })
                        seen_users.add(user_id)
                
                print(f"✅ Found {len(result)} users with category preference")
                return result
            else:
                # Get all users without filter
                response = self.supabase.table('users').select('id, email, name, subscription_plan').execute()
                return response.data or []
                
        except Exception as e:
            print(f"❌ Error getting all users: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def get_admin_stats(self) -> dict:
        """Get admin statistics with proper error handling"""
        try:
            # Real database queries
                # Get user count
                users_response = self.supabase.table('users').select('id', count='exact').execute()
                total_users = users_response.count or 0
                
                # Get application stats
                apps_response = self.supabase.table('job_applications').select('status', count='exact').execute()
                total_applications = apps_response.count or 0
                
                # Get status breakdown
                pending_response = self.supabase.table('job_applications').select('id', count='exact').eq('status', 'queued').execute()
                pending_applications = pending_response.count or 0
                
                completed_response = self.supabase.table('job_applications').select('id', count='exact').eq('status', 'completed').execute()
                completed_applications = completed_response.count or 0
                
                captcha_response = self.supabase.table('captcha_sessions').select('id', count='exact').eq('status', 'pending').execute()
                pending_captchas = captcha_response.count or 0
                
                return {
                    "total_users": total_users,
                    "total_applications": total_applications,
                    "pending_applications": pending_applications,
                    "completed_applications": completed_applications,
                    "pending_captchas": pending_captchas
                }
        except Exception as e:
            print(f"Error getting admin stats: {e}")
            return {
                "total_users": 0,
                "total_applications": 0,
                "pending_applications": 0,
                "completed_applications": 0,
                "pending_captchas": 0
            }

    async def get_job_urls(self, category_id: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
        """Get job URLs with proper category name joining"""
        try:
            # Real database queries
                # Build query with proper joins
                query = (
                    self.supabase.table('job_urls_master')
                    .select('*, job_categories(category_name)')
                )
                
                if category_id:
                    query = query.eq('category_id', category_id)
                if status:
                    query = query.eq('status', status)
                
                response = query.execute()
                
                # Flatten the response to match expected format
                formatted_urls = []
                for url_data in response.data or []:
                    category_info = url_data.pop('job_categories', {})
                    url_data['category_name'] = category_info.get('category_name') if category_info else None
                    formatted_urls.append(url_data)
                
                return formatted_urls
        except Exception as e:
            print(f"Error getting job URLs: {e}")
            return []
    
    async def get_captcha_session(self, session_id: str) -> Optional[dict]:
        """Get CAPTCHA session by ID"""
        try:
            response = self.supabase.table('captcha_sessions').select('*').eq('id', session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting CAPTCHA session: {e}")
            return None
    
    async def create_captcha_session(self, captcha_data: dict) -> dict:
        """Create a new CAPTCHA session"""
        try:
            response = self.supabase.table('captcha_sessions').insert(captcha_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating CAPTCHA session: {e}")
            return None
    
    async def update_captcha_status(self, session_id: str, status: str) -> bool:
        """Update CAPTCHA session status"""
        try:
            response = self.supabase.table('captcha_sessions').update({
                'status': status,
                'solved_at': datetime.utcnow().isoformat() if status == 'solved' else None
            }).eq('id', session_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating CAPTCHA status: {e}")
            return False
    
    # USER Q&A CACHE FUNCTIONS
    async def get_user_qa_cache(self, user_id: str, question_text: str = None) -> List[dict]:
        """Get user's Q&A cache entries"""
        try:
            query = self.supabase.table('user_qa_cache').select('*').eq('user_id', user_id)
            
            if question_text:
                query = query.eq('question_text', question_text)
            
            response = query.execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting user Q&A cache: {e}")
            return []
    
    async def save_user_qa_cache(self, cache_data: dict) -> dict:
        """Save entry to user's Q&A cache"""
        try:
            # Check if entry already exists
            existing = await self.get_user_qa_cache(
                cache_data['user_id'], 
                cache_data['question_text']
            )
            
            if existing:
                # Update existing entry
                response = self.supabase.table('user_qa_cache').update({
                    'answer_text': cache_data['answer_text'],
                    'confidence_score': cache_data.get('confidence_score', 0.8),
                    'usage_count': existing[0].get('usage_count', 0) + 1,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', existing[0]['id']).execute()
            else:
                # Create new entry
                response = self.supabase.table('user_qa_cache').insert(cache_data).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving user Q&A cache: {e}")
            return None
    
    async def update_qa_cache_usage(self, user_id: str, question_text: str) -> bool:
        """Update usage count for Q&A cache entry"""
        try:
            # First get the current entry
            cache_entries = await self.get_user_qa_cache(user_id, question_text)
            if not cache_entries:
                return False
            
            entry = cache_entries[0]
            new_usage_count = entry.get('usage_count', 0) + 1
            
            response = self.supabase.table('user_qa_cache').update({
                'usage_count': new_usage_count,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', entry['id']).execute()
            
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating Q&A cache usage: {e}")
            return False
    
    # SITE FIELD PATTERNS FUNCTIONS
    async def get_site_field_patterns(self, site_domain: str, field_label: str = None) -> List[dict]:
        """Get site-specific field patterns"""
        try:
            query = self.supabase.table('site_field_patterns').select('*').eq('site_domain', site_domain)
            
            if field_label:
                query = query.eq('field_label', field_label)
            
            response = query.execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting site field patterns: {e}")
            return []
    
    async def save_site_field_pattern(self, pattern_data: dict) -> dict:
        """Save or update site field pattern"""
        try:
            # Check if pattern already exists
            existing = await self.get_site_field_patterns(
                pattern_data['site_domain'],
                pattern_data['field_label']
            )
            
            if existing:
                # Update existing pattern
                pattern = existing[0]
                common_answers = pattern.get('common_answers', {})
                
                # Update common answers
                new_answer = pattern_data.get('new_answer')
                if new_answer:
                    if isinstance(common_answers, dict):
                        common_answers[new_answer] = common_answers.get(new_answer, 0) + 1
                    else:
                        common_answers = {new_answer: 1}
                
                response = self.supabase.table('site_field_patterns').update({
                    'common_answers': common_answers,
                    'usage_frequency': pattern.get('usage_frequency', 0) + 1
                }).eq('id', pattern['id']).execute()
            else:
                # Create new pattern
                response = self.supabase.table('site_field_patterns').insert(pattern_data).execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving site field pattern: {e}")
            return None
    
    # APPLICATION Q&A HISTORY FUNCTIONS
    async def save_application_qa_history(self, history_data: dict) -> dict:
        """Save Q&A interaction to application history"""
        try:
            response = self.supabase.table('application_qa_history').insert(history_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving application Q&A history: {e}")
            return None
    
    async def get_application_qa_history(self, application_id: str) -> List[dict]:
        """Get Q&A history for an application"""
        try:
            response = self.supabase.table('application_qa_history').select('*').eq('application_id', application_id).execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting application Q&A history: {e}")
            return []
    
    async def get_user_qa_history(self, user_id: str, limit: int = 50) -> List[dict]:
        """Get Q&A history for a user across all applications"""
        try:
            response = (
                self.supabase.table('application_qa_history')
                .select('*')
                .eq('user_id', user_id)
                .order('created_at', desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            print(f"Error getting user Q&A history: {e}")
            return []
    
    # ENHANCED APPLICATION FUNCTIONS
    async def get_applications_by_status(self, status: str, limit: int = 10) -> List[dict]:
        """Get applications by status"""
        try:
            response = (
                self.supabase.table('job_applications')
                .select('*')
                .eq('status', status)
                .order('created_at')
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            print(f"Error getting applications by status: {e}")
            return []
    
    async def update_application_status(self, app_id: str, status: str, error_message: str = None) -> bool:
        """Update application status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if error_message:
                update_data['error_message'] = error_message
            
            if status == 'processing':
                update_data['processing_started_at'] = datetime.utcnow().isoformat()
            elif status == 'completed':
                update_data['submitted_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('job_applications').update(update_data).eq('id', app_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating application status: {e}")
            return False
    
    # ANALYTICS AND STATS FUNCTIONS
    async def get_qa_system_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get Q&A system statistics"""
        try:
            stats = {}
            
            if user_id:
                # User-specific stats
                cache_response = self.supabase.table('user_qa_cache').select('id', count='exact').eq('user_id', user_id).execute()
                history_response = self.supabase.table('application_qa_history').select('id', count='exact').eq('user_id', user_id).execute()
                
                stats['user_cache_entries'] = getattr(cache_response, 'count', 0)
                stats['user_qa_interactions'] = getattr(history_response, 'count', 0)
            else:
                # System-wide stats
                total_cache = self.supabase.table('user_qa_cache').select('id', count='exact').execute()
                total_history = self.supabase.table('application_qa_history').select('id', count='exact').execute()
                total_patterns = self.supabase.table('site_field_patterns').select('id', count='exact').execute()
                
                stats['total_cache_entries'] = getattr(total_cache, 'count', 0)
                stats['total_qa_interactions'] = getattr(total_history, 'count', 0)
                stats['total_site_patterns'] = getattr(total_patterns, 'count', 0)
            
            return stats
        except Exception as e:
            print(f"Error getting Q&A system stats: {e}")
            return {}
    
    async def get_most_common_questions(self, limit: int = 10) -> List[dict]:
        """Get most commonly asked questions across all users"""
        try:
            # This would require a more complex query in production
            # For now, we'll get the most used cache entries
            response = (
                self.supabase.table('user_qa_cache')
                .select('question_text, usage_count')
                .order('usage_count', desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            print(f"Error getting most common questions: {e}")
            return []
    
    async def get_site_success_patterns(self, site_domain: str) -> Dict[str, Any]:
        """Get successful patterns for a specific site"""
        try:
            # Get all patterns for the site
            patterns_response = self.supabase.table('site_field_patterns').select('*').eq('site_domain', site_domain).execute()
            
            # Get successful applications for the site
            apps_response = (
                self.supabase.table('job_applications')
                .select('status')
                .like('job_url', f'%{site_domain}%')
                .execute()
            )
            
            patterns = patterns_response.data or []
            applications = apps_response.data or []
            
            total_apps = len(applications)
            successful_apps = len([app for app in applications if app['status'] == 'completed'])
            
            return {
                'site_domain': site_domain,
                'field_patterns_count': len(patterns),
                'total_applications': total_apps,
                'successful_applications': successful_apps,
                'success_rate': (successful_apps / total_apps * 100) if total_apps > 0 else 0,
                'patterns': patterns
            }
        except Exception as e:
            print(f"Error getting site success patterns: {e}")
            return {}
    
    # SEARCH AND SIMILARITY FUNCTIONS
    async def search_similar_questions(self, question_text: str, user_id: str = None, limit: int = 5) -> List[dict]:
        """Search for similar questions in the Q&A cache"""
        try:
            # This is a simplified version - in production you'd want semantic search
            query = self.supabase.table('user_qa_cache').select('*')
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            # For now, we'll do a simple text search
            # In production, you'd implement vector similarity search
            response = query.ilike('question_text', f'%{question_text}%').limit(limit).execute()
            
            return response.data or []
        except Exception as e:
            print(f"Error searching similar questions: {e}")
            return []
    
    # CLEANUP AND MAINTENANCE FUNCTIONS
    async def cleanup_old_captcha_sessions(self, days_old: int = 1) -> int:
        """Clean up old CAPTCHA sessions"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            response = (
                self.supabase.table('captcha_sessions')
                .delete()
                .lt('created_at', cutoff_date.isoformat())
                .execute()
            )
            
            deleted_count = len(response.data) if response.data else 0
            print(f"🧹 Cleaned up {deleted_count} old CAPTCHA sessions")
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up CAPTCHA sessions: {e}")
            return 0
    
    async def optimize_qa_cache(self, user_id: str) -> Dict[str, int]:
        """Optimize user's Q&A cache by removing low-confidence, unused entries"""
        try:
            # Get entries with low confidence and low usage
            response = (
                self.supabase.table('user_qa_cache')
                .select('*')
                .eq('user_id', user_id)
                .lt('confidence_score', 0.3)
                .eq('usage_count', 1)
                .execute()
            )
            
            low_quality_entries = response.data or []
            
            # Delete low-quality entries
            deleted_count = 0
            for entry in low_quality_entries:
                delete_response = (
                    self.supabase.table('user_qa_cache')
                    .delete()
                    .eq('id', entry['id'])
                    .execute()
                )
                if delete_response.data:
                    deleted_count += 1
            
            # Get remaining count
            remaining_response = (
                self.supabase.table('user_qa_cache')
                .select('id', count='exact')
                .eq('user_id', user_id)
                .execute()
            )
            
            remaining_count = getattr(remaining_response, 'count', 0)
            
            return {
                'deleted_entries': deleted_count,
                'remaining_entries': remaining_count
            }
        except Exception as e:
            print(f"Error optimizing Q&A cache: {e}")
            return {'deleted_entries': 0, 'remaining_entries': 0}


db = DatabaseConnection()