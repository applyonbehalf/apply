# main.py (FIXED VERSION)
import time
import sys
import os
from src.browser_handler import BrowserHandler
from src.knowledge_base import KnowledgeBase
from src.ai_engine import AIEngine
from src import utils
from src import semantic_cache 
from src import history_manager
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, NoSuchElementException
from selenium.webdriver.common.by import By

def process_page_elements(browser, ai, kb):
    """Processes all form elements using the smarter browser handler."""
    q_history = history_manager.load_history()
    
    # --- NEW: Click "Attach resume" link before processing ---
    try:
        attach_link = browser.driver.find_element(By.PARTIAL_LINK_TEXT, "Attach resume")
        if attach_link.is_displayed():
            print("Found 'Attach resume' link, clicking to reveal file input.")
            attach_link.click()
            time.sleep(1)
    except NoSuchElementException:
        pass # No link found, continue
        
    form_fields = browser.get_form_elements_fully()
    if not form_fields:
        print("Could not find any form fields on the page.")
        return 0

    filled_count = 0
    all_kb_keys = kb.get_all_keys()
    
    for field in form_fields:
        label = field.get('label', '')
        if not label: continue

        field_type = field.get('type')
        is_required = field.get('required', False)
        print(f"\nProcessing field: '{label}' (Type: {field_type}, Required: {is_required})")

        final_answer = None

        # Check history first
        if label in q_history:
            final_answer = q_history[label]
            print(f"HISTORY: Found answer for '{label}'")
        else:
            if field_type not in ['radio', 'checkbox']:
                # FIXED: Use the corrected semantic cache functions
                answer_key = semantic_cache.get_field_mapping(label) or ai.find_best_match_for_label(label, all_kb_keys)
                if answer_key: 
                    semantic_cache.add_field_mapping(label, answer_key)
                final_answer = kb.get_info(answer_key) if answer_key else None
            else: # For radio/checkbox
                options = [browser._get_label_for_element(e) for e in field.get('elements', [])]
                final_answer = ai.answer_yes_no_question(label, kb._data) or ai.make_a_choice(label, options, kb._data)
        
        if final_answer is not None:
            q_history[label] = final_answer
            print(f"  ➡️ Determined Answer: '{final_answer}'")
            
            if field_type in ['radio', 'checkbox']:
                if browser.click_choice_button(field['elements'], final_answer):
                    print(f"✅ Clicked choice '{final_answer}' for '{label}'")
                    filled_count += 1
            elif field_type == 'dropdown':
                browser.select_dropdown_option_by_text(field['element'], final_answer)
                print(f"✅ Selected '{final_answer}' for '{label}'")
                filled_count += 1
            else: # Text, file, etc.
                if isinstance(final_answer, list): 
                    final_answer = ", ".join(final_answer)
                browser.fill_text_input_slowly(field['element'], final_answer)
                filled_count += 1
        elif is_required:
            print(f"❌ Warning: No answer found for required field: '{label}'")

    history_manager.save_history(q_history)
    return filled_count

def handle_alert(browser):
    try:
        alert = browser.driver.switch_to.alert
        alert_text = alert.text
        print(f"\n--- ALERT DETECTED ---: {alert_text}")
        alert.accept()
        return alert_text
    except NoAlertPresentException:
        return None

def main():
    print("--- Starting IntelliApply Bot (v18 - FINAL SUBMISSION FIX) ---")
    kb = KnowledgeBase()
    ai = AIEngine()
    browser = BrowserHandler()
    
    if not all([kb._data, ai.model, browser.driver]):
        sys.exit("A critical component failed to initialize. Exiting.")
    
    try:
        job_url = "https://aqueity.applytojob.com/apply/Appyvb1yAu/Jr-SOC-Engineer?source=LinkedIn"
        browser.navigate_to_url(job_url)
        initial_url = browser.driver.current_url
        browser.handle_cookie_banner()
        
        process_page_elements(browser, ai, kb)

        # Enhanced CAPTCHA detection and handling
        captcha_solved = False
        try:
            captcha_elements = browser.driver.find_elements(By.XPATH, 
                "//iframe[contains(@src, 'recaptcha')] | //*[contains(@class, 'recaptcha')] | //*[@id='recaptcha'] | //*[contains(@class, 'g-recaptcha')]")
            
            if captcha_elements:
                print("\n🚨 CAPTCHA DETECTED! Please solve it manually.")
                print("The script will wait for you to solve the CAPTCHA...")
                
                for i in range(12):  # Check every 5 seconds for 60 seconds
                    time.sleep(5)
                    
                    # Check if CAPTCHA is solved
                    try:
                        page_source = browser.driver.page_source.lower()
                        if 'recaptcha-checkbox-checked' in page_source or 'solved' in page_source:
                            print("✅ CAPTCHA appears to be solved!")
                            captcha_solved = True
                            break
                    except Exception:
                        pass
                    
                    if i % 2 == 0:
                        print(f"⏳ Still waiting... ({60 - (i*5)} seconds remaining)")
                
                if not captcha_solved:
                    print("⚠️ CAPTCHA may still be unsolved, but continuing anyway...")
            else:
                print("\nNo CAPTCHA detected.")
                captcha_solved = True
                
        except Exception as e:
            print(f"Error checking CAPTCHA: {e}")
            captcha_solved = True

        # Enhanced submit button detection and clicking
        print("\n🔍 Looking for submit button...")
        
        submit_button = None
        submit_patterns = [
            "//a[@id='resumator-submit-resume']",  # Specific ID from the error
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit application')]",
            "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit application')]",
            "//*[contains(@class, 'btn') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
            "//input[@type='submit']",
            "//button[@type='submit']"
        ]
        
        for pattern in submit_patterns:
            try:
                elements = browser.driver.find_elements(By.XPATH, pattern)
                for element in elements:
                    if element.is_displayed():
                        submit_button = element
                        print(f"✅ Found submit button: {element.tag_name} with text: '{element.text}'")
                        break
                if submit_button:
                    break
            except Exception as e:
                continue
        
        if submit_button:
            print(f"\n🎯 Attempting to submit application...")
            print(f"   Element: {submit_button.tag_name}")
            print(f"   Text: '{submit_button.text}'")
            print(f"   ID: '{submit_button.get_attribute('id')}'")
            
            # Store current state to check for changes
            current_url = browser.driver.current_url
            
            try:
                # Remove any overlays that might be blocking the click
                browser.driver.execute_script("""
                    // Remove any overlay elements
                    var overlays = document.querySelectorAll('div[style*="position: fixed"][style*="z-index"]');
                    overlays.forEach(function(overlay) {
                        if (overlay.style.zIndex > 1000000) {
                            overlay.remove();
                        }
                    });
                """)
                
                # Wait a moment for overlays to be removed
                time.sleep(1)
                
                # Scroll to submit button and ensure it's visible
                browser.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                time.sleep(2)
                
                # Try multiple submission methods
                submission_successful = False
                
                # Method 1: Direct JavaScript submission if it's a form
                try:
                    browser.driver.execute_script("""
                        var submitButton = arguments[0];
                        var form = submitButton.closest('form');
                        if (form) {
                            form.submit();
                        }
                    """, submit_button)
                    print("✅ Attempted form submission via JavaScript")
                    time.sleep(3)
                    
                    # Check if URL changed
                    new_url = browser.driver.current_url
                    if new_url != current_url:
                        print("🎉 URL changed after submission - likely successful!")
                        submission_successful = True
                    
                except Exception as e:
                    print(f"Form submission failed: {e}")
                
                # Method 2: Click the actual submit button if form submission didn't work
                if not submission_successful:
                    try:
                        # Force click with JavaScript
                        browser.driver.execute_script("""
                            arguments[0].click();
                        """, submit_button)
                        print("✅ Clicked submit button with JavaScript")
                        time.sleep(3)
                        
                        # Check for URL change again
                        new_url = browser.driver.current_url
                        if new_url != current_url:
                            print("🎉 URL changed after button click - submission successful!")
                            submission_successful = True
                            
                    except Exception as e:
                        print(f"Button click failed: {e}")
                
                # Method 3: Trigger submit event directly
                if not submission_successful:
                    try:
                        browser.driver.execute_script("""
                            var submitButton = arguments[0];
                            var event = new Event('click', {bubbles: true, cancelable: true});
                            submitButton.dispatchEvent(event);
                        """, submit_button)
                        print("✅ Triggered click event via JavaScript")
                        time.sleep(3)
                        
                        new_url = browser.driver.current_url
                        if new_url != current_url:
                            print("🎉 URL changed after event trigger - submission successful!")
                            submission_successful = True
                            
                    except Exception as e:
                        print(f"Event trigger failed: {e}")
                
                # Check for submission success indicators
                final_url = browser.driver.current_url
                page_content = browser.driver.page_source.lower()
                
                # Look for success indicators
                success_keywords = ['thank you', 'thanks', 'submitted', 'application received', 'success', 'confirmation']
                success_found = any(keyword in page_content for keyword in success_keywords)
                url_changed = final_url != current_url
                
                if url_changed and ('thank' in final_url.lower() or 'success' in final_url.lower() or 'confirm' in final_url.lower()):
                    print("\n🎉 --- APPLICATION SUBMITTED SUCCESSFULLY! ---")
                    print(f"   Final URL: {final_url}")
                elif success_found:
                    print("\n🎉 --- APPLICATION SUBMITTED SUCCESSFULLY! ---")
                    print("   Success indicators found on page")
                elif url_changed:
                    print("\n✅ --- APPLICATION LIKELY SUBMITTED ---")
                    print(f"   URL changed from: {current_url}")
                    print(f"   URL changed to: {final_url}")
                else:
                    print("\n⚠️ --- SUBMISSION STATUS UNCLEAR ---")
                    print("   No clear success indicators found")
                    print("   You may want to check manually")
                    
                    # Show current form state
                    form_still_visible = 'submit application' in page_content
                    if form_still_visible:
                        print("   ⚠️ Form appears to still be visible - submission may have failed")
                    else:
                        print("   ✅ Form no longer visible - submission may have succeeded")
                
            except Exception as e:
                print(f"❌ Error during submission process: {e}")
                
        else:
            print("\n❌ Could not find submit button")
            
        # Keep browser open longer to see final state
        print("\n⏸️ Keeping browser open for 15 seconds to observe final state...")
        time.sleep(15)
        
    except Exception as e:
        print(f"\n💥 --- A CRITICAL ERROR OCCURRED ---")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔒 Closing browser...")
        browser.close_browser()
def get_all_keys_recursive(data_dict, parent_key=''):
    keys = []
    for k, v in data_dict.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            keys.extend(get_all_keys_recursive(v, new_key))
        else:
            keys.append(new_key)
    return keys

# Add the method to KnowledgeBase class
KnowledgeBase.get_all_keys = lambda self: get_all_keys_recursive(self._data)

if __name__ == "__main__":
    main()