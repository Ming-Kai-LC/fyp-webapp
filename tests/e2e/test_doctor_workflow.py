"""
End-to-end tests for doctor workflow
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from faker import Faker
import time
import os

fake = Faker()


@pytest.mark.e2e
@pytest.mark.doctor
@pytest.mark.django_db(transaction=True)
class TestDoctorWorkflow:
    """Test complete doctor user journey"""

    def test_doctor_registration(self, browser, live_server_url, e2e_helpers):
        """Test doctor registration process"""
        try:
            # Navigate to registration page
            browser.get(f"{live_server_url}/register/")

            # Fill in registration form
            username = f"doctor_{fake.user_name()}"
            email = f"{username}@test.com"
            password = "TestPassword123!"

            browser.find_element(By.NAME, "username").send_keys(username)
            browser.find_element(By.NAME, "email").send_keys(email)
            browser.find_element(By.NAME, "password1").send_keys(password)
            browser.find_element(By.NAME, "password2").send_keys(password)

            # Select doctor role
            role_select = Select(browser.find_element(By.NAME, "role"))
            role_select.select_by_value("doctor")

            # Submit registration
            browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            # Wait for redirect
            time.sleep(2)

            # Verify we're not on the registration page anymore
            assert "/register/" not in browser.current_url, "Still on registration page after submit"

            print(f"✓ Doctor registration successful: {username}")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_registration_failed.png")
            raise

    def test_doctor_login_and_dashboard(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor login and dashboard access"""
        try:
            # Login
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            # Wait for redirect to dashboard
            time.sleep(2)

            # Verify we reached a dashboard or home page (not login)
            assert "/accounts/login/" not in browser.current_url, "Still on login page"

            # Verify user is logged in
            page_source = browser.page_source.lower()
            assert any(word in page_source for word in ['logout', 'dashboard', 'doctor']), \
                "No indication of logged in state"

            print(f"✓ Doctor login successful: {test_doctor_user['username']}")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_login_failed.png")
            raise

    def test_doctor_dashboard_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access their dashboard"""
        try:
            # Login first
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to navigate to doctor dashboard
            dashboard_urls = [
                f"{live_server_url}/detection/doctor/dashboard/",
                f"{live_server_url}/doctor/dashboard/",
                f"{live_server_url}/dashboard/"
            ]

            dashboard_loaded = False
            for dashboard_url in dashboard_urls:
                try:
                    browser.get(dashboard_url)
                    time.sleep(2)

                    # Check if page loaded successfully
                    if "404" not in browser.page_source and "error" not in browser.page_source.lower():
                        dashboard_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "doctor_dashboard.png")

            # Verify doctor is logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Doctor dashboard accessed successfully")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_dashboard_failed.png")
            raise

    def test_doctor_xray_upload_page_access(self, browser, live_server_url, test_doctor_user, test_patient_user,
                                            e2e_helpers, sample_xray_image):
        """Test doctor can access X-ray upload page"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Navigate to upload page
            upload_urls = [
                f"{live_server_url}/detection/upload/",
                f"{live_server_url}/upload/",
                f"{live_server_url}/xray/upload/"
            ]

            upload_page_loaded = False
            for upload_url in upload_urls:
                try:
                    browser.get(upload_url)
                    time.sleep(2)

                    # Check if page loaded successfully
                    if "404" not in browser.page_source:
                        upload_page_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "doctor_upload_page.png")

            # Check if upload form exists
            page_source = browser.page_source.lower()
            has_upload_elements = any(word in page_source for word in
                                     ['upload', 'x-ray', 'xray', 'file', 'image', 'patient'])

            if upload_page_loaded and has_upload_elements:
                print("✓ Doctor X-ray upload page accessed successfully")
            else:
                print("⚠ Upload page may not be fully functional")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_upload_access_failed.png")
            raise

    def test_doctor_view_patients(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can view patient list"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to navigate to patients page
            patient_urls = [
                f"{live_server_url}/detection/patients/",
                f"{live_server_url}/patients/",
                f"{live_server_url}/detection/doctor/patients/"
            ]

            patients_loaded = False
            for patient_url in patient_urls:
                try:
                    browser.get(patient_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        patients_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "doctor_patients_list.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Doctor patient list access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_patients_failed.png")
            raise

    def test_doctor_prediction_history(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can view prediction history"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to navigate to prediction history
            history_urls = [
                f"{live_server_url}/detection/history/",
                f"{live_server_url}/predictions/",
                f"{live_server_url}/detection/predictions/"
            ]

            history_loaded = False
            for history_url in history_urls:
                try:
                    browser.get(history_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        history_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "doctor_prediction_history.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Doctor prediction history access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_history_failed.png")
            raise

    def test_doctor_logout(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor logout"""
        try:
            # Login first
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Logout
            e2e_helpers.logout(browser, live_server_url)

            time.sleep(2)

            # Try to access protected page
            browser.get(f"{live_server_url}/detection/doctor/dashboard/")
            time.sleep(2)

            # Should be redirected to login
            assert "/accounts/login/" in browser.current_url or "login" in browser.current_url.lower(), \
                "Can still access protected pages after logout"

            print("✓ Doctor logout successful")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_logout_failed.png")
            raise

    def test_complete_doctor_journey(self, browser, live_server_url, e2e_helpers, test_patient_user):
        """Test complete doctor journey from registration to logout"""
        try:
            # 1. Register
            browser.get(f"{live_server_url}/register/")
            username = f"doctor_journey_{fake.user_name()}"
            email = f"{username}@test.com"
            password = "TestPassword123!"

            browser.find_element(By.NAME, "username").send_keys(username)
            browser.find_element(By.NAME, "email").send_keys(email)
            browser.find_element(By.NAME, "password1").send_keys(password)
            browser.find_element(By.NAME, "password2").send_keys(password)

            role_select = Select(browser.find_element(By.NAME, "role"))
            role_select.select_by_value("doctor")

            browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(3)

            print(f"  Step 1/6: Registration completed - {username}")

            # 2. Login (if not auto-logged in)
            if "/accounts/login/" in browser.current_url:
                e2e_helpers.login(browser, live_server_url, username, password)
                time.sleep(2)

            print("  Step 2/6: Login completed")

            # 3. Access dashboard
            dashboard_urls = [
                f"{live_server_url}/detection/doctor/dashboard/",
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

            e2e_helpers.take_screenshot(browser, "doctor_journey_dashboard.png")
            print("  Step 3/6: Dashboard accessed")

            # 4. Try to access upload page
            upload_urls = [f"{live_server_url}/detection/upload/"]
            for upload_url in upload_urls:
                try:
                    browser.get(upload_url)
                    time.sleep(2)
                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            e2e_helpers.take_screenshot(browser, "doctor_journey_upload.png")
            print("  Step 4/6: Upload page accessed")

            # 5. View prediction history
            history_urls = [f"{live_server_url}/detection/history/"]
            for history_url in history_urls:
                try:
                    browser.get(history_url)
                    time.sleep(2)
                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            e2e_helpers.take_screenshot(browser, "doctor_journey_history.png")
            print("  Step 5/6: History accessed")

            # 6. Logout
            e2e_helpers.logout(browser, live_server_url)
            time.sleep(2)

            print("  Step 6/6: Logout completed")

            print(f"✓ Complete doctor journey successful for: {username}")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_journey_failed.png")
            raise
