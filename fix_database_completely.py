# fix_database_completely.py - Complete fix for database connection
import os
import shutil

def backup_and_fix_database():
    """Backup and fix the database connection file"""
    
    db_file = "backend/database/connection.py"
    backup_file = "backend/database/connection.py.backup"
    
    print("🔧 Fixing Database Connection")
    print("=" * 40)
    
    if not os.path.exists(db_file):
        print(f"❌ File not found: {db_file}")
        return False
    
    # Create backup
    shutil.copy2(db_file, backup_file)
    print(f"📁 Backup created: {backup_file}")
    
    # Read current content
    with open(db_file, 'r') as f:
        content = f.read()
    
    # Check if already fixed
    if "get_applications_by_status" in content and "create_notification" in content:
        print("✅ Database methods already exist")
        return True
    
    # New complete database connection with all missing methods
    new_content = '''# database/connection.py - Complete version with all methods
from supabase import create_client, Client
from config import settings
import asyncio
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

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
db = DatabaseConnection()'''
    
    # Write the new content
    with open(db_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Database connection file updated")
    return True

def main():
    """Main function"""
    if backup_and_fix_database():
        print("\n🎯 Database fixed successfully!")
        print("\nNext steps:")
        print("1. Restart your server (Ctrl+C and restart)")
        print("2. Run: python quick_fix_and_test.py")
        print("3. The bot should now work properly!")
    else:
        print("\n❌ Failed to fix database")

if __name__ == "__main__":
    main()