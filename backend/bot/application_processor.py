# bot/application_processor.py - Main application processing engine
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from database.connection import db
from bot.enhanced_browser_handler import EnhancedBrowserHandler
from bot.enhanced_ai_engine import EnhancedAIEngine
from services.notification_service import NotificationService
import uuid

class ApplicationProcessor:
    """Main engine for processing job applications"""
    
    def __init__(self, headless: bool = True, max_concurrent: int = 1):
        self.headless = headless
        self.max_concurrent = max_concurrent
        self.ai_engine = EnhancedAIEngine()
        self.notification_service = NotificationService()
        self.active_sessions = {}
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'captcha_required': 0,
            'start_time': datetime.utcnow()
        }
        self.is_running = False
        
        print(f"🤖 Application Processor initialized (max_concurrent: {max_concurrent})")
    
    async def start_processing(self):
        """Start the main processing loop"""
        self.is_running = True
        print("🚀 Starting application processing engine...")
        
        try:
            while self.is_running:
                await self._process_queue_batch()
                await asyncio.sleep(5)  # Check queue every 5 seconds
                
        except KeyboardInterrupt:
            print("\n⏸️ Processing stopped by user")
        except Exception as e:
            print(f"❌ Processing engine error: {e}")
        finally:
            await self._cleanup_all_sessions()
            self.is_running = False
    
    async def stop_processing(self):
        """Stop the processing engine"""
        self.is_running = False
        await self._cleanup_all_sessions()
        print("⏹️ Application processing stopped")
    
    async def _process_queue_batch(self):
        """Process a batch of applications from the queue"""
        try:
            # Get queued applications
            applications = await db.get_applications_by_status('queued', limit=self.max_concurrent)
            
            if not applications:
                return  # No applications to process
            
            print(f"📋 Found {len(applications)} applications to process")
            
            # Process applications concurrently
            tasks = []
            for application in applications:
                if len(self.active_sessions) < self.max_concurrent:
                    task = asyncio.create_task(self._process_single_application(application))
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            print(f"❌ Queue batch processing error: {e}")
    
    async def _process_single_application(self, application: Dict[str, Any]):
        """Process a single job application"""
        app_id = application['id']
        user_id = application['user_id']
        job_url = application['job_url']
        
        print(f"\n🎯 Processing application {app_id[:8]}...")
        print(f"   User: {user_id}")
        print(f"   URL: {job_url}")
        
        browser = None
        try:
            # Update status to processing
            await db.update_application_status(app_id, 'processing')
            
            # Get user profile
            profile = await db.get_profile_by_id(application['profile_id'])
            if not profile:
                raise Exception("Profile not found")
            
            # Create browser session
            browser = EnhancedBrowserHandler(user_id=user_id, headless=self.headless)
            self.active_sessions[app_id] = browser
            
            # Navigate to job page
            navigation_success = await browser.navigate_to_job(job_url, app_id)
            if not navigation_success:
                raise Exception("Failed to navigate to job page")
            
            # Scan form elements
            form_fields = await browser.scan_form_elements()
            if not form_fields:
                raise Exception("No form fields found on page")
            
            print(f"📝 Found {len(form_fields)} form fields to fill")
            
            # Fill form fields
            filled_count = await self._fill_form_fields(browser, form_fields, profile['profile_data'])
            print(f"✅ Successfully filled {filled_count} fields")
            
            # Check for CAPTCHA
            captcha_info = await browser.check_for_captcha()
            if captcha_info:
                await self._handle_captcha(app_id, captcha_info, browser)
                return  # Wait for manual CAPTCHA resolution
            
            # Submit application
            submission_result = await browser.submit_application()
            
            if submission_result['success']:
                await self._handle_successful_application(app_id, user_id, submission_result)
            else:
                await self._handle_failed_application(app_id, user_id, submission_result['error'])
                
        except Exception as e:
            await self._handle_failed_application(app_id, user_id, str(e))
            
        finally:
            # Cleanup browser session
            if browser:
                browser.close()
            if app_id in self.active_sessions:
                del self.active_sessions[app_id]
    
    async def _fill_form_fields(self, browser: EnhancedBrowserHandler, form_fields: List[Dict], profile_data: Dict) -> int:
        """Fill all form fields using AI"""
        filled_count = 0
        
        for field in form_fields:
            try:
                field_label = field.get('label', '')
                field_type = field.get('type', '')
                
                if not field_label:
                    continue
                
                print(f"📝 Processing field: {field_label} ({field_type})")
                
                if field_type in ['radio', 'checkbox']:
                    # Handle choice fields
                    if 'elements' in field:
                        # Get available options
                        options = []
                        for element in field['elements']:
                            option_label = await browser._get_field_label(element)
                            if option_label:
                                options.append(option_label)
                        
                        if options:
                            choice = self.ai_engine.make_intelligent_choice(field_label, options, profile_data)
                            if choice:
                                success = await browser.fill_choice_field(field, choice)
                                if success:
                                    filled_count += 1
                
                elif field_type == 'textarea':
                    # Generate essay response
                    essay = self.ai_engine.generate_essay_response(field_label, profile_data)
                    if essay:
                        success = await browser.fill_field(field, essay)
                        if success:
                            filled_count += 1
                
                else:
                    # Regular fields (text, email, etc.)
                    field_path = self.ai_engine.map_field_to_profile_data(field_label, profile_data)
                    if field_path:
                        value = self.ai_engine.get_profile_value(field_path, profile_data)
                        if value:
                            success = await browser.fill_field(field, value)
                            if success:
                                filled_count += 1
                        else:
                            print(f"⚠️ No value found for field path: {field_path}")
                    else:
                        print(f"⚠️ No mapping found for field: {field_label}")
                
                # Small delay between fields
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error filling field {field_label}: {e}")
                continue
        
        return filled_count
    
    async def _handle_captcha(self, app_id: str, captcha_info: Dict, browser: EnhancedBrowserHandler):
        """Handle CAPTCHA detection"""
        try:
            print(f"🚨 CAPTCHA detected for application {app_id[:8]}")
            
            # Update application status
            await db.update_application_status(app_id, 'captcha_required')
            
            # Create CAPTCHA session
            captcha_session_data = {
                'id': str(uuid.uuid4()),
                'application_id': app_id,
                'screenshot_url': captcha_info.get('screenshot_url'),
                'page_url': captcha_info.get('page_url'),
                'status': 'pending'
            }
            
            captcha_session = await db.create_captcha_session(captcha_session_data)
            
            # Send notification
            await self.notification_service.send_captcha_alert(captcha_session)
            
            # Wait for CAPTCHA resolution
            await self._wait_for_captcha_resolution(captcha_session['id'], app_id, browser)
            
            self.processing_stats['captcha_required'] += 1
            
        except Exception as e:
            print(f"❌ CAPTCHA handling error: {e}")
            await self._handle_failed_application(app_id, None, f"CAPTCHA handling error: {e}")
    
    async def _wait_for_captcha_resolution(self, captcha_session_id: str, app_id: str, browser: EnhancedBrowserHandler):
        """Wait for CAPTCHA to be resolved manually"""
        timeout = 900  # 15 minutes
        check_interval = 10  # Check every 10 seconds
        
        for _ in range(0, timeout, check_interval):
            try:
                # Check CAPTCHA status
                captcha_session = await db.get_captcha_session(captcha_session_id)
                
                if captcha_session['status'] == 'solved':
                    print(f"✅ CAPTCHA solved for application {app_id[:8]}")
                    
                    # Continue with application submission
                    submission_result = await browser.submit_application()
                    
                    if submission_result['success']:
                        await self._handle_successful_application(app_id, None, submission_result)
                    else:
                        await self._handle_failed_application(app_id, None, submission_result['error'])
                    
                    return
                
                elif captcha_session['status'] in ['expired', 'skipped']:
                    print(f"⏭️ CAPTCHA {captcha_session['status']} for application {app_id[:8]}")
                    await self._handle_failed_application(app_id, None, f"CAPTCHA {captcha_session['status']}")
                    return
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Error checking CAPTCHA status: {e}")
                break
        
        # Timeout reached
        print(f"⏰ CAPTCHA timeout for application {app_id[:8]}")
        await db.update_captcha_status(captcha_session_id, 'expired')
        await self._handle_failed_application(app_id, None, "CAPTCHA timeout")
    
    async def _handle_successful_application(self, app_id: str, user_id: str, result: Dict):
        """Handle successful application submission"""
        try:
            # Update application status
            await db.update_application_status(app_id, 'completed')
            
            # Update user's application count
            if user_id:
                user = await db.get_user_by_id(user_id)
                if user:
                    await db.update_user(user_id, {
                        'applications_used': user['applications_used'] + 1
                    })
            
            # Send success notification
            await self.notification_service.send_application_success(app_id, user_id)
            
            # Update stats
            self.processing_stats['successful'] += 1
            self.processing_stats['total_processed'] += 1
            
            print(f"🎉 Application {app_id[:8]} completed successfully")
            
        except Exception as e:
            print(f"❌ Error handling successful application: {e}")
    
    async def _handle_failed_application(self, app_id: str, user_id: str, error_message: str):
        """Handle failed application"""
        try:
            # Update application status
            await db.update_application_status(app_id, 'failed', error_message)
            
            # Send failure notification
            await self.notification_service.send_application_failure(app_id, user_id, error_message)
            
            # Update stats
            self.processing_stats['failed'] += 1
            self.processing_stats['total_processed'] += 1
            
            print(f"❌ Application {app_id[:8]} failed: {error_message}")
            
        except Exception as e:
            print(f"❌ Error handling failed application: {e}")
    
    async def _cleanup_all_sessions(self):
        """Cleanup all active browser sessions"""
        print("🧹 Cleaning up browser sessions...")
        
        for app_id, browser in self.active_sessions.items():
            try:
                browser.close()
            except Exception as e:
                print(f"⚠️ Error closing session {app_id}: {e}")
        
        self.active_sessions.clear()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.processing_stats.copy()
        stats['uptime_seconds'] = (datetime.utcnow() - stats['start_time']).total_seconds()
        stats['active_sessions'] = len(self.active_sessions)
        stats['ai_cache_stats'] = self.ai_engine.get_cache_stats()
        
        if stats['total_processed'] > 0:
            stats['success_rate'] = (stats['successful'] / stats['total_processed']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    async def process_single_url(self, user_id: str, profile_id: str, job_url: str) -> Dict[str, Any]:
        """Process a single application manually (for testing)"""
        try:
            # Create temporary application record
            app_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'profile_id': profile_id,
                'job_url': job_url,
                'status': 'processing'
            }
            
            # Process the application
            await self._process_single_application(app_data)
            
            return {'success': True, 'message': 'Application processed successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}