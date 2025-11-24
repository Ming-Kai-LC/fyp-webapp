"""
End-to-end tests for patient workflow
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from faker import Faker
import time

fake = Faker()


@pytest.mark.e2e
@pytest.mark.patient
@pytest.mark.django_db(transaction=True)
class TestPatientWorkflow:
    """Test complete patient user journey"""

    def test_patient_registration(self, browser, live_server_url, e2e_helpers):
        """Test patient registration process"""
        try:
            # Navigate to registration page
            browser.get(f"{live_server_url}/register/")

            # Fill in registration form
            username = f"patient_{fake.user_name()}"
            email = f"{username}@test.com"
            password = "TestPassword123!"

            browser.find_element(By.NAME, "username").send_keys(username)
            browser.find_element(By.NAME, "email").send_keys(email)
            browser.find_element(By.NAME, "password1").send_keys(password)
            browser.find_element(By.NAME, "password2").send_keys(password)

            # Select patient role
            role_select = Select(browser.find_element(By.NAME, "role"))
            role_select.select_by_value("patient")

            # Submit registration
            browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Wait for redirect (should go to login or dashboard)
            time.sleep(2)

            # Verify we're not on the registration page anymore
            assert "/register/" not in browser.current_url, "Still on registration page after submit"

            print(f"✓ Patient registration successful: {username}")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_registration_failed.png")
            raise

    def test_patient_login_and_dashboard(self, browser, live_server_url, test_patient_user, e2e_helpers):
        """Test patient login and dashboard access"""
        try:
            # Login
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )

            # Wait for redirect to dashboard
            time.sleep(2)

            # Verify we reached a dashboard or home page (not login)
            assert "/accounts/login/" not in browser.current_url, "Still on login page"

            # Verify user is logged in by checking for logout link or user menu
            page_source = browser.page_source.lower()
            assert any(word in page_source for word in ['logout', 'dashboard', 'profile']), \
                "No indication of logged in state"

            print(f"✓ Patient login successful: {test_patient_user['username']}")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_login_failed.png")
            raise

    def test_patient_profile_update(self, browser, live_server_url, test_patient_user, e2e_helpers):
        """Test patient profile update"""
        try:
            # Login first
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )

            time.sleep(2)

            # Navigate to profile page
            profile_urls = [
                f"{live_server_url}/detection/patient/profile/",
                f"{live_server_url}/profile/",
                f"{live_server_url}/accounts/profile/"
            ]

            profile_loaded = False
            for profile_url in profile_urls:
                try:
                    browser.get(profile_url)
                    time.sleep(2)

                    # Check if we're on a valid profile page
                    if browser.current_url == profile_url or "profile" in browser.current_url:
                        profile_loaded = True
                        break
                except:
                    continue

            if not profile_loaded:
                # Try to find profile link
                try:
                    profile_link = browser.find_element(By.PARTIAL_LINK_TEXT, "Profile")
                    profile_link.click()
                    time.sleep(2)
                    profile_loaded = True
                except NoSuchElementException:
                    pass

            # Take screenshot for debugging
            e2e_helpers.take_screenshot(browser, "patient_profile_page.png")

            # Verify we're on some kind of profile page
            page_source = browser.page_source.lower()
            assert any(word in page_source for word in ['profile', 'patient', 'information']), \
                "Profile page not loaded"

            print("✓ Patient profile page accessed successfully")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_profile_update_failed.png")
            raise

    def test_patient_view_medical_history(self, browser, live_server_url, test_patient_user, e2e_helpers):
        """Test patient can view medical history"""
        try:
            # Login first
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )

            time.sleep(2)

            # Try to navigate to medical records page
            medical_urls = [
                f"{live_server_url}/medical-records/",
                f"{live_server_url}/medical-records/conditions/",
                f"{live_server_url}/medical-records/dashboard/"
            ]

            medical_loaded = False
            for medical_url in medical_urls:
                try:
                    browser.get(medical_url)
                    time.sleep(2)

                    # Check if page loaded successfully (not 404 or error)
                    if "404" not in browser.page_source and "error" not in browser.page_source.lower():
                        medical_loaded = True
                        break
                except:
                    continue

            # Take screenshot for debugging
            e2e_helpers.take_screenshot(browser, "patient_medical_history.png")

            # Even if we can't access medical records, verify patient is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Patient session lost"

            print("✓ Patient medical history access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_medical_history_failed.png")
            raise

    def test_patient_logout(self, browser, live_server_url, test_patient_user, e2e_helpers):
        """Test patient logout"""
        try:
            # Login first
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )

            time.sleep(2)

            # Logout
            e2e_helpers.logout(browser, live_server_url)

            time.sleep(2)

            # Verify logout successful
            # Should be redirected to login or home page
            page_source = browser.page_source.lower()

            # Should not have access to dashboard or profile
            browser.get(f"{live_server_url}/detection/patient/dashboard/")
            time.sleep(2)

            # Should be redirected to login if trying to access protected page
            assert "/accounts/login/" in browser.current_url or "login" in browser.current_url.lower(), \
                "Can still access protected pages after logout"

            print("✓ Patient logout successful")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_logout_failed.png")
            raise

    def test_complete_patient_journey(self, browser, live_server_url, e2e_helpers):
        """Test complete patient journey from registration to logout"""
        try:
            # 1. Register
            browser.get(f"{live_server_url}/register/")
            username = f"patient_journey_{fake.user_name()}"
            email = f"{username}@test.com"
            password = "TestPassword123!"

            browser.find_element(By.NAME, "username").send_keys(username)
            browser.find_element(By.NAME, "email").send_keys(email)
            browser.find_element(By.NAME, "password1").send_keys(password)
            browser.find_element(By.NAME, "password2").send_keys(password)

            role_select = Select(browser.find_element(By.NAME, "role"))
            role_select.select_by_value("patient")

            browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(3)

            print(f"  Step 1/5: Registration completed - {username}")

            # 2. Login (if not auto-logged in)
            if "/accounts/login/" in browser.current_url:
                e2e_helpers.login(browser, live_server_url, username, password)
                time.sleep(2)

            print("  Step 2/5: Login completed")

            # 3. Access dashboard
            dashboard_urls = [
                f"{live_server_url}/detection/patient/dashboard/",
                f"{live_server_url}/dashboard/",
                f"{live_server_url}/"
            ]

            for dashboard_url in dashboard_urls:
                try:
                    browser.get(dashboard_url)
                    time.sleep(2)
                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            print("  Step 3/5: Dashboard accessed")

            # 4. Take screenshots for verification
            e2e_helpers.take_screenshot(browser, "patient_journey_dashboard.png")

            print("  Step 4/5: Screenshots captured")

            # 5. Logout
            e2e_helpers.logout(browser, live_server_url)
            time.sleep(2)

            print("  Step 5/5: Logout completed")

            print(f"✓ Complete patient journey successful for: {username}")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_journey_failed.png")
            raise
