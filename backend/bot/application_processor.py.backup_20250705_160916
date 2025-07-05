# bot/application_processor.py - UPDATED WITH Q&A SYSTEM INTEGRATION

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from database.connection import db
from bot.enhanced_browser_handler import EnhancedBrowserHandler
from bot.enhanced_ai_engine import EnhancedAIEngine
from bot.qa_system import QASystem  # NEW: Import Q&A system
from services.notification_service import NotificationService
import uuid

class ApplicationProcessor:
    """Main engine for processing job applications with Q&A system integration"""
    
    def __init__(self, headless: bool = True, max_concurrent: int = 1):
        self.headless = headless
        self.max_concurrent = max_concurrent
        self.ai_engine = EnhancedAIEngine()
        self.qa_system = QASystem()  # NEW: Initialize Q&A system
        self.notification_service = NotificationService()
        self.active_sessions = {}
        self.processing_stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'captcha_required': 0,
            'qa_cache_hits': 0,  # NEW: Track Q&A cache performance
            'manual_inputs_required': 0,  # NEW: Track manual inputs
            'start_time': datetime.utcnow()
        }
        self.is_running = False
        
        print(f"🤖 Application Processor with Q&A System initialized (max_concurrent: {max_concurrent})")
    
    async def start_processing(self):
        """Start the main processing loop"""
        self.is_running = True
        print("🚀 Starting application processing engine with Q&A system...")
        
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
        """Process a single job application with Q&A system integration"""
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
            
            # Get user profile with enhanced fetching
            profile_data = await self._get_user_profile_from_database(user_id, application['profile_id'])
            if not profile_data:
                raise Exception("Profile not found")
            
            # Extract site domain for Q&A system
            site_domain = self._extract_domain(job_url)
            print(f"🌐 Site domain: {site_domain}")
            
            # Create browser session
            browser = EnhancedBrowserHandler(user_id=user_id, headless=self.headless)
            self.active_sessions[app_id] = browser
            
            # Navigate to job page
            navigation_success = await browser.navigate_to_job(job_url, app_id)
            if not navigation_success:
                raise Exception("Failed to navigate to job page")
            
            # Scan form elements
            form_fields = await browser.scan_form_elements()
            
            # Check if CAPTCHA was detected
            if form_fields and len(form_fields) == 1 and form_fields[0].get('__captcha_detected__'):
                captcha_info = form_fields[0]['captcha_info']
                print(f"🚨 CAPTCHA detected - waiting for manual solution...")
                
                # Wait for CAPTCHA to be solved
                captcha_solved = await browser.wait_for_captcha_solution(captcha_info, timeout=300)
                
                if captcha_solved:
                    print("✅ CAPTCHA solved - continuing with form filling...")
                    # Re-scan form fields after CAPTCHA is solved
                    form_fields = await browser.scan_form_elements(skip_captcha_check=True)
                else:
                    raise Exception("CAPTCHA timeout - manual intervention required")
            
            if not form_fields:
                raise Exception("No form fields found on page")
            
            print(f"📝 Found {len(form_fields)} form fields to fill")
            
            # Fill form fields using Q&A system
            filled_count = await self._fill_form_fields_with_qa(browser, form_fields, profile_data, user_id, app_id, site_domain)
            print(f"✅ Successfully filled {filled_count} fields using Q&A system")
            
            # Check for CAPTCHA after filling
            captcha_info = await browser.check_for_captcha()
            if captcha_info:
                await self._handle_captcha(app_id, captcha_info, browser)
                return  # Wait for manual CAPTCHA resolution
            
            # Submit application
            submission_result = await browser.submit_application()
            
            if submission_result['success']:
                await self._handle_successful_application(app_id, user_id, submission_result)
                # Update site patterns based on successful submission
                await self._update_site_patterns_after_success(site_domain, form_fields, user_id)
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
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for site-specific patterns"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return "unknown.com"
    
    async def _get_user_profile_from_database(self, user_id: str, profile_id: str = None) -> dict:
        """Fetch user profile data from Supabase database"""
        try:
            print(f"🔍 Fetching profile for user: {user_id}")
            
            if profile_id:
                # Get specific profile
                profile = await db.get_profile_by_id(profile_id)
                print(f"📋 Retrieved specific profile: {profile_id}")
            else:
                # Get user's profiles and use the first active one
                profiles = await db.get_user_profiles(user_id)
                profile = profiles[0] if profiles else None
                print(f"📋 Retrieved user profiles: {len(profiles) if profiles else 0} found")
            
            if profile and 'profile_data' in profile:
                profile_data = profile['profile_data']
                user_name = profile_data.get('personal_info', {}).get('full_name', 'Unknown User')
                user_email = profile_data.get('personal_info', {}).get('email', 'Unknown Email')
                
                print(f"✅ Profile loaded successfully:")
                print(f"   Name: {user_name}")
                print(f"   Email: {user_email}")
                print(f"   Profile: {profile.get('profile_name', 'Default')}")
                
                return profile_data
            else:
                print(f"⚠️ No profile data found for user {user_id}")
                return self._get_fallback_profile_data()
                
        except Exception as e:
            print(f"❌ Error fetching profile from database: {e}")
            return self._get_fallback_profile_data()
    
    def _get_fallback_profile_data(self) -> dict:
        """Fallback profile data if database fetch fails"""
        return {
            "personal_info": {
                "legal_first_name": "John",
                "legal_last_name": "Doe",
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "address_line_1": "123 Main Street",
                "city": "San Francisco",
                "state_province": "CA",
                "zip_postal_code": "94102"
            },
            "experience": {
                "total_years_professional_experience": "3-5 years",
                "salary_expectation": "$80,000 - $100,000",
                "it_managed_services_experience": "3-5 years",
                "information_security_experience": "2-3 years"
            },
            "preferences": {
                "work_preference": "Hybrid"
            },
            "eligibility": {
                "work_authorization": "authorized",
                "visa_sponsorship_required": False,
                "visa_sponsorship": "No"
            }
        }
    
    async def _fill_form_fields_with_qa(self, browser: EnhancedBrowserHandler, form_fields: List[Dict], 
                                       profile_data: Dict, user_id: str, application_id: str, site_domain: str) -> int:
        """Fill form fields using the Q&A hierarchical system"""
        filled_count = 0
        
        for field in form_fields:
            try:
                # Get field information
                field_label = await self._get_enhanced_field_label(browser, field)
                field_type = field.get('type', 'text')
                
                if not field_label or field_label == 'Unknown field':
                    print(f"⚠️ Skipping field with unknown label")
                    continue
                
                print(f"📝 Processing field: {field_label} ({field_type})")
                
                # Use Q&A system for hierarchical lookup
                answer = await self.qa_system.get_field_answer_hierarchical(
                    user_id=user_id,
                    application_id=application_id,
                    field_label=field_label,
                    field_type=field_type,
                    site_domain=site_domain,
                    profile_data=profile_data
                )
                
                if answer and answer != "MANUAL_INPUT_REQUIRED":
                    # Fill the field based on type
                    success = await self._fill_field_by_type(browser, field, answer, field_type)
                    if success:
                        filled_count += 1
                        # Update site patterns for successful fills
                        await self.qa_system.update_site_patterns(site_domain, field_label, answer, field_type)
                        
                        # Track Q&A cache hits
                        if answer:  # If we got an answer, it came from one of our levels
                            self.processing_stats['qa_cache_hits'] += 1
                    else:
                        print(f"❌ Failed to fill field: {field_label}")
                
                elif answer == "MANUAL_INPUT_REQUIRED":
                    print(f"🚨 Manual input required for: {field_label}")
                    self.processing_stats['manual_inputs_required'] += 1
                    # In production, this would trigger a UI notification
                    
                else:
                    print(f"⚠️ No answer found for field: {field_label}")
                
                # Small delay between fields
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing field {field.get('label', 'unknown')}: {e}")
                continue
        
        return filled_count
    
    async def _get_enhanced_field_label(self, browser: EnhancedBrowserHandler, field: Dict[str, Any]) -> str:
        """Get enhanced field label using multiple detection methods"""
        element = field.get('element')
        if not element:
            return 'Unknown field'
        
        # Try multiple methods to get field label
        label_methods = [
            lambda: element.get_attribute('placeholder'),
            lambda: element.get_attribute('aria-label'),
            lambda: element.get_attribute('title'),
            lambda: element.get_attribute('name'),
            lambda: element.get_attribute('id'),
        ]
        
        # Try to find associated label element
        try:
            # Look for label element by 'for' attribute
            field_id = element.get_attribute('id')
            if field_id:
                label_element = browser.driver.find_element(By.CSS_SELECTOR, f'label[for="{field_id}"]')
                if label_element:
                    label_text = label_element.text.strip()
                    if label_text:
                        return label_text
        except:
            pass
        
        # Try to find label by proximity (parent/sibling elements)
        try:
            # Check parent elements for text
            parent = element.find_element(By.XPATH, '..')
            parent_text = parent.text.strip()
            if parent_text and len(parent_text) < 100:  # Reasonable label length
                # Clean up the text (remove the field value if present)
                lines = parent_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.isdigit() and len(line) < 50:
                        return line
        except:
            pass
        
        # Fall back to attribute-based detection
        for method in label_methods:
            try:
                label = method()
                if label and label.strip():
                    return label.strip()
            except:
                continue
        
        return field.get('label', 'Unknown field')
    
    async def _fill_field_by_type(self, browser: EnhancedBrowserHandler, field: Dict[str, Any], 
                                 answer: str, field_type: str) -> bool:
        """Fill field based on its type using the provided answer"""
        try:
            element = field['element']
            
            # Scroll to element
            browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            await asyncio.sleep(0.5)
            
            if field_type in ['text', 'email', 'tel', 'url', 'search', 'password']:
                # Text input fields
                element.clear()
                element.send_keys(str(answer))
                return True
                
            elif field_type == 'textarea':
                # Textarea fields
                element.clear()
                element.send_keys(str(answer))
                return True
                
            elif field_type == 'select-one':
                # Dropdown fields
                from selenium.webdriver.support.ui import Select
                select = Select(element)
                
                # Try to select by visible text first
                try:
                    select.select_by_visible_text(str(answer))
                    return True
                except:
                    # Try partial text match
                    for option in select.options:
                        if str(answer).lower() in option.text.lower():
                            select.select_by_visible_text(option.text)
                            return True
                    
                    # If no match, try to select by value
                    try:
                        select.select_by_value(str(answer))
                        return True
                    except:
                        pass
                
                return False
                
            elif field_type in ['radio', 'checkbox']:
                # Radio buttons and checkboxes
                return await self._handle_choice_field(browser, field, answer)
                
            elif field_type == 'file':
                # File upload fields
                # For now, skip file uploads unless we have a valid file path
                if answer and answer.startswith('/') and answer.endswith('.pdf'):
                    element.send_keys(answer)
                    return True
                return False
                
            else:
                # Default to text input for unknown types
                element.clear()
                element.send_keys(str(answer))
                return True
                
        except Exception as e:
            print(f"❌ Error filling field: {e}")
            return False
    
    async def _handle_choice_field(self, browser: EnhancedBrowserHandler, field: Dict[str, Any], answer: str) -> bool:
        """Handle radio buttons and checkboxes"""
        try:
            # If field has multiple elements (radio group), find the right one
            if 'elements' in field:
                for element in field['elements']:
                    element_label = await self._get_element_label(browser, element)
                    if element_label and str(answer).lower() in element_label.lower():
                        element.click()
                        return True
            else:
                # Single checkbox
                element = field['element']
                should_check = str(answer).lower() in ['yes', 'true', '1', 'on', 'checked']
                
                if should_check and not element.is_selected():
                    element.click()
                    return True
                elif not should_check and element.is_selected():
                    element.click()
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error handling choice field: {e}")
            return False
    
    async def _get_element_label(self, browser: EnhancedBrowserHandler, element) -> str:
        """Get label for a specific element"""
        try:
            # Try various methods to get element label
            label_text = (
                element.get_attribute('aria-label') or
                element.get_attribute('title') or
                element.get_attribute('value') or
                element.text.strip()
            )
            
            # If no direct label, look for nearby text
            if not label_text:
                try:
                    parent = element.find_element(By.XPATH, '..')
                    label_text = parent.text.strip()
                except:
                    pass
            
            return label_text or 'Unknown'
            
        except Exception as e:
            return 'Unknown'
    
    async def _update_site_patterns_after_success(self, site_domain: str, form_fields: List[Dict], user_id: str):
        """Update site patterns after successful application submission"""
        try:
            print(f"📊 Updating site patterns for successful submission on {site_domain}")
            
            # This could be enhanced to learn from successful patterns
            # For now, we just log the success
            
        except Exception as e:
            print(f"❌ Error updating site patterns: {e}")
    
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
        """Get processing statistics including Q&A metrics"""
        stats = self.processing_stats.copy()
        stats['uptime_seconds'] = (datetime.utcnow() - stats['start_time']).total_seconds()
        stats['active_sessions'] = len(self.active_sessions)
        stats['ai_cache_stats'] = self.ai_engine.get_cache_stats()
        
        if stats['total_processed'] > 0:
            stats['success_rate'] = (stats['successful'] / stats['total_processed']) * 100
            stats['qa_cache_hit_rate'] = (stats['qa_cache_hits'] / stats['total_processed']) * 100
        else:
            stats['success_rate'] = 0
            stats['qa_cache_hit_rate'] = 0
        
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
    
    async def get_qa_system_stats(self, user_id: str) -> Dict[str, Any]:
        """Get Q&A system statistics for a user"""
        try:
            return await self.qa_system.get_user_qa_stats(user_id)
        except Exception as e:
            print(f"❌ Error getting Q&A stats: {e}")
            return {'error': str(e)}