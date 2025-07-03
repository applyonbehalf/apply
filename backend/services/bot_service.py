# services/bot_service.py - Bot service manager and API integration
import asyncio
from typing import Dict, Any, Optional
from bot.application_processor import ApplicationProcessor
from database.connection import db
from services.notification_service import NotificationService
import uuid

class BotService:
    """Service layer for managing the application processing bot"""
    
    def __init__(self):
        self.processor = None
        self.notification_service = NotificationService()
        self.is_running = False
        
    async def start_bot(self, headless: bool = True, max_concurrent: int = 1) -> Dict[str, Any]:
        """Start the application processing bot"""
        try:
            if self.is_running:
                return {'success': False, 'message': 'Bot is already running'}
            
            print("🤖 Starting IntelliApply Bot Service...")
            
            # Create processor
            self.processor = ApplicationProcessor(headless=headless, max_concurrent=max_concurrent)
            
            # Start processing in background
            asyncio.create_task(self.processor.start_processing())
            
            self.is_running = True
            
            # Send system alert
            await self.notification_service.send_system_alert("IntelliApply Bot started successfully", "info")
            
            return {
                'success': True,
                'message': 'Bot started successfully',
                'config': {
                    'headless': headless,
                    'max_concurrent': max_concurrent
                }
            }
            
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
            return {'success': False, 'message': f'Failed to start bot: {str(e)}'}
    
    async def stop_bot(self) -> Dict[str, Any]:
        """Stop the application processing bot"""
        try:
            if not self.is_running or not self.processor:
                return {'success': False, 'message': 'Bot is not running'}
            
            print("⏹️ Stopping IntelliApply Bot Service...")
            
            # Stop processor
            await self.processor.stop_processing()
            
            self.is_running = False
            self.processor = None
            
            # Send system alert
            await self.notification_service.send_system_alert("IntelliApply Bot stopped", "info")
            
            return {'success': True, 'message': 'Bot stopped successfully'}
            
        except Exception as e:
            print(f"❌ Error stopping bot: {e}")
            return {'success': False, 'message': f'Failed to stop bot: {str(e)}'}
    
    async def get_bot_status(self) -> Dict[str, Any]:
        """Get current bot status and statistics"""
        try:
            if not self.is_running or not self.processor:
                return {
                    'running': False,
                    'message': 'Bot is not running'
                }
            
            stats = self.processor.get_processing_stats()
            
            return {
                'running': True,
                'stats': stats,
                'active_sessions': len(self.processor.active_sessions),
                'message': 'Bot is running normally'
            }
            
        except Exception as e:
            print(f"❌ Error getting bot status: {e}")
            return {
                'running': False,
                'error': str(e),
                'message': 'Error retrieving bot status'
            }
    
    async def add_urls_to_queue(self, user_id: str, profile_id: str, urls: list, batch_name: str = None) -> Dict[str, Any]:
        """Add job URLs to the processing queue"""
        try:
            # Validate user and profile
            user = await db.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            profile = await db.get_profile_by_id(profile_id)
            if not profile or profile['user_id'] != user_id:
                return {'success': False, 'message': 'Profile not found or access denied'}
            
            # Check user's application limit
            if user['applications_used'] + len(urls) > user['applications_limit']:
                remaining = user['applications_limit'] - user['applications_used']
                return {
                    'success': False, 
                    'message': f'Would exceed application limit. You have {remaining} applications remaining.'
                }
            
            # Create batch
            batch_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'batch_name': batch_name or f"Batch {len(urls)} jobs",
                'urls': urls,
                'profile_id': profile_id,
                'total_count': len(urls),
                'status': 'pending'
            }
            
            batch = await db.create_batch(batch_data)
            
            # Create individual applications
            applications_created = 0
            for url in urls:
                app_data = {
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'profile_id': profile_id,
                    'batch_id': batch['id'],
                    'job_url': url,
                    'status': 'queued',
                    'priority': 0
                }
                
                app = await db.create_application(app_data)
                if app:
                    applications_created += 1
            
            return {
                'success': True,
                'message': f'Added {applications_created} applications to queue',
                'batch_id': batch['id'],
                'applications_created': applications_created
            }
            
        except Exception as e:
            print(f"❌ Error adding URLs to queue: {e}")
            return {'success': False, 'message': f'Failed to add URLs: {str(e)}'}
    
    async def process_single_application(self, user_id: str, profile_id: str, job_url: str) -> Dict[str, Any]:
        """Process a single application immediately (for testing)"""
        try:
            if not self.processor:
                return {'success': False, 'message': 'Bot is not running'}
            
            # Validate user and profile
            user = await db.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            profile = await db.get_profile_by_id(profile_id)
            if not profile or profile['user_id'] != user_id:
                return {'success': False, 'message': 'Profile not found or access denied'}
            
            # Check application limit
            if user['applications_used'] >= user['applications_limit']:
                return {'success': False, 'message': 'Application limit exceeded'}
            
            # Process the application
            result = await self.processor.process_single_url(user_id, profile_id, job_url)
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing single application: {e}")
            return {'success': False, 'message': f'Failed to process application: {str(e)}'}
    
    async def pause_user_applications(self, user_id: str) -> Dict[str, Any]:
        """Pause all applications for a specific user"""
        try:
            # Update all queued applications to paused status
            # Note: You'll need to add this function to your database connection
            updated_count = await db.pause_user_applications(user_id)
            
            return {
                'success': True,
                'message': f'Paused {updated_count} applications for user',
                'updated_count': updated_count
            }
            
        except Exception as e:
            print(f"❌ Error pausing user applications: {e}")
            return {'success': False, 'message': f'Failed to pause applications: {str(e)}'}
    
    async def resume_user_applications(self, user_id: str) -> Dict[str, Any]:
        """Resume all paused applications for a specific user"""
        try:
            # Update all paused applications back to queued status
            updated_count = await db.resume_user_applications(user_id)
            
            return {
                'success': True,
                'message': f'Resumed {updated_count} applications for user',
                'updated_count': updated_count
            }
            
        except Exception as e:
            print(f"❌ Error resuming user applications: {e}")
            return {'success': False, 'message': f'Failed to resume applications: {str(e)}'}
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        try:
            # Get applications by status
            queued = await db.get_applications_by_status('queued')
            processing = await db.get_applications_by_status('processing')
            captcha_required = await db.get_applications_by_status('captcha_required')
            
            # Get pending CAPTCHAs
            pending_captchas = await db.get_pending_captchas()
            
            return {
                'queued': len(queued),
                'processing': len(processing),
                'captcha_required': len(captcha_required),
                'pending_captchas': len(pending_captchas),
                'total_pending': len(queued) + len(processing) + len(captcha_required)
            }
            
        except Exception as e:
            print(f"❌ Error getting queue status: {e}")
            return {'error': str(e)}
    
    async def get_user_queue_status(self, user_id: str) -> Dict[str, Any]:
        """Get queue status for a specific user"""
        try:
            # Get user's applications by status
            all_apps = await db.get_user_applications(user_id, limit=1000)
            
            status_counts = {
                'queued': 0,
                'processing': 0,
                'captcha_required': 0,
                'completed': 0,
                'failed': 0,
                'total': len(all_apps)
            }
            
            for app in all_apps:
                status = app.get('status', 'unknown')
                if status in status_counts:
                    status_counts[status] += 1
            
            # Calculate success rate
            completed = status_counts['completed']
            total_processed = completed + status_counts['failed']
            success_rate = (completed / total_processed * 100) if total_processed > 0 else 0
            
            return {
                **status_counts,
                'success_rate': round(success_rate, 1)
            }
            
        except Exception as e:
            print(f"❌ Error getting user queue status: {e}")
            return {'error': str(e)}

# Global bot service instance
bot_service = BotService()