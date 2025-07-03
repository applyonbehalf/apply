# services/notification_service.py - Fixed notification system (Python 3.13 compatible)
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from database.connection import db
from config import settings
import uuid

class NotificationService:
    """Service for handling notifications (database only for now)"""
    
    def __init__(self):
        # Disable email/SMS for now to avoid import issues
        self.email_enabled = False
        self.sms_enabled = False
        print(f"📢 Notification Service initialized (Database notifications only)")
    
    async def send_captcha_alert(self, captcha_session: Dict[str, Any]):
        """Send CAPTCHA alert notification"""
        try:
            # Get application details
            application = await db.get_application_by_id(captcha_session['application_id'])
            if not application:
                print("❌ Application not found for CAPTCHA alert")
                return
            
            # Get user details
            user = await db.get_user_by_id(application['user_id'])
            if not user:
                print("❌ User not found for CAPTCHA alert")
                return
            
            # Create notification data
            notification_data = {
                'title': '🚨 CAPTCHA Required',
                'message': f"CAPTCHA needs to be solved for {application.get('company_name', 'Unknown Company')} application",
                'data': {
                    'captcha_session_id': captcha_session['id'],
                    'application_id': application['id'],
                    'job_title': application.get('job_title'),
                    'company_name': application.get('company_name'),
                    'solve_url': f"https://applyonbehalf.com/solve-captcha/{captcha_session['id']}"
                },
                'type': 'captcha_required',
                'user_id': None,  # Admin notification
                'is_admin_notification': True
            }
            
            # Save to database
            await self._create_notification(notification_data)
            
            print(f"📢 CAPTCHA alert saved to database for application {application['id'][:8]}")
            
            # Console alert (instead of email/SMS)
            print(f"🚨 CAPTCHA ALERT: {user['name']} needs CAPTCHA solved for {application.get('company_name', 'Unknown Company')}")
            print(f"   Solve at: http://localhost:8000/solve-captcha/{captcha_session['id']}")
            
        except Exception as e:
            print(f"❌ Error sending CAPTCHA alert: {e}")
    
    async def send_application_success(self, app_id: str, user_id: str):
        """Send application success notification"""
        try:
            # Get application details
            application = await db.get_application_by_id(app_id)
            if not application:
                return
            
            # Create notification
            notification_data = {
                'title': '✅ Application Submitted',
                'message': f"Successfully applied to {application.get('company_name', 'Unknown Company')}",
                'data': {
                    'application_id': app_id,
                    'job_title': application.get('job_title'),
                    'company_name': application.get('company_name'),
                    'submitted_at': datetime.utcnow().isoformat()
                },
                'type': 'application_completed',
                'user_id': user_id
            }
            
            await self._create_notification(notification_data)
            print(f"📢 Success notification saved for application {app_id[:8]}")
            
        except Exception as e:
            print(f"❌ Error sending success notification: {e}")
    
    async def send_application_failure(self, app_id: str, user_id: str, error_message: str):
        """Send application failure notification"""
        try:
            # Get application details
            application = await db.get_application_by_id(app_id)
            if not application:
                return
            
            # Create notification
            notification_data = {
                'title': '❌ Application Failed',
                'message': f"Failed to apply to {application.get('company_name', 'Unknown Company')}: {error_message[:100]}",
                'data': {
                    'application_id': app_id,
                    'job_title': application.get('job_title'),
                    'company_name': application.get('company_name'),
                    'error_message': error_message,
                    'failed_at': datetime.utcnow().isoformat()
                },
                'type': 'application_failed',
                'user_id': user_id
            }
            
            await self._create_notification(notification_data)
            print(f"📢 Failure notification saved for application {app_id[:8]}")
            
        except Exception as e:
            print(f"❌ Error sending failure notification: {e}")
    
    async def send_batch_completion(self, batch_id: str, user_id: str):
        """Send batch completion notification"""
        try:
            # Get batch details
            batch = await db.get_batch_by_id(batch_id)
            if not batch:
                return
            
            # Create notification
            notification_data = {
                'title': '📋 Batch Completed',
                'message': f"Batch '{batch['batch_name']}' completed: {batch['successful_count']}/{batch['total_count']} successful",
                'data': {
                    'batch_id': batch_id,
                    'batch_name': batch['batch_name'],
                    'total_count': batch['total_count'],
                    'successful_count': batch['successful_count'],
                    'failed_count': batch['failed_count'],
                    'completed_at': datetime.utcnow().isoformat()
                },
                'type': 'batch_completed',
                'user_id': user_id
            }
            
            await self._create_notification(notification_data)
            print(f"📢 Batch completion notification saved for {batch_id[:8]}")
            
        except Exception as e:
            print(f"❌ Error sending batch completion notification: {e}")
    
    async def send_quota_exceeded(self, user_id: str):
        """Send quota exceeded notification"""
        try:
            user = await db.get_user_by_id(user_id)
            if not user:
                return
            
            notification_data = {
                'title': '⚠️ Application Limit Reached',
                'message': f"You've reached your monthly limit of {user['applications_limit']} applications",
                'data': {
                    'user_id': user_id,
                    'applications_limit': user['applications_limit'],
                    'reset_date': user['reset_date'].isoformat() if user.get('reset_date') else None
                },
                'type': 'quota_exceeded',
                'user_id': user_id
            }
            
            await self._create_notification(notification_data)
            print(f"📢 Quota exceeded notification saved for user {user_id[:8]}")
            
        except Exception as e:
            print(f"❌ Error sending quota notification: {e}")
    
    async def _create_notification(self, notification_data: Dict[str, Any]):
        """Create notification in database"""
        try:
            notification_data['id'] = str(uuid.uuid4())
            await db.create_notification(notification_data)
        except Exception as e:
            print(f"❌ Error creating notification: {e}")
    
    async def send_system_alert(self, message: str, severity: str = 'info'):
        """Send system alert to admins"""
        try:
            notification_data = {
                'title': f'🔧 System Alert ({severity.upper()})',
                'message': message,
                'data': {
                    'severity': severity,
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'application_processor'
                },
                'type': 'system_alert',
                'user_id': None,  # Admin notification
                'is_admin_notification': True
            }
            
            await self._create_notification(notification_data)
            print(f"🔧 System alert: {message}")
            
        except Exception as e:
            print(f"❌ Error sending system alert: {e}")
    
    async def get_unread_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get unread notifications for a user"""
        try:
            return await db.get_user_notifications(user_id, unread_only=True)
        except Exception as e:
            print(f"❌ Error getting unread notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            return await db.mark_notification_read(notification_id)
        except Exception as e:
            print(f"❌ Error marking notification as read: {e}")
            return False
    
    async def send_test_notification(self, user_id: str = None):
        """Send a test notification"""
        try:
            notification_data = {
                'title': '🧪 Test Notification',
                'message': 'This is a test notification to verify the system is working',
                'data': {
                    'test': True,
                    'timestamp': datetime.utcnow().isoformat()
                },
                'type': 'system_alert',
                'user_id': user_id,
                'is_admin_notification': user_id is None
            }
            
            await self._create_notification(notification_data)
            print("🧪 Test notification sent")
            return True
            
        except Exception as e:
            print(f"❌ Error sending test notification: {e}")
            return False