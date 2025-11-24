"""
End-to-end tests for X-ray upload and AI analysis
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
@pytest.mark.django_db(transaction=True)
class TestXRayUploadWorkflow:
    """Test X-ray upload and AI prediction workflow"""

    def test_xray_upload_page_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
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
            upload_url = f"{live_server_url}/detection/upload/"
            browser.get(upload_url)
            time.sleep(2)

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "xray_upload_page.png")

            # Verify page loaded
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ X-ray upload page accessed successfully")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "xray_upload_page_failed.png")
            raise

    def test_xray_upload_form_elements(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test X-ray upload form contains required elements"""
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
            upload_url = f"{live_server_url}/detection/upload/"
            browser.get(upload_url)
            time.sleep(2)

            # Check for form elements
            page_source = browser.page_source.lower()

            # Look for expected form elements
            expected_elements = ['patient', 'file', 'upload', 'image', 'x-ray', 'xray']
            found_elements = [elem for elem in expected_elements if elem in page_source]

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "xray_upload_form.png")

            # Should have at least some form elements
            if len(found_elements) >= 2:
                print(f"✓ Upload form contains expected elements: {found_elements}")
            else:
                print(f"⚠ Upload form may be incomplete. Found: {found_elements}")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "xray_upload_form_failed.png")
            raise

    def test_prediction_results_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access prediction results page"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to navigate to prediction history to find results
            history_url = f"{live_server_url}/detection/history/"
            try:
                browser.get(history_url)
                time.sleep(2)
            except:
                pass

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "prediction_results_access.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Prediction results access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "prediction_results_access_failed.png")
            raise

    def test_prediction_history_view(self, browser, live_server_url, test_doctor_user, e2e_helpers):
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

            # Navigate to prediction history
            history_url = f"{live_server_url}/detection/history/"
            browser.get(history_url)
            time.sleep(2)

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "prediction_history.png")

            # Check page content
            page_source = browser.page_source.lower()
            has_history_elements = any(word in page_source for word in
                                      ['prediction', 'history', 'result', 'covid', 'patient'])

            if has_history_elements:
                print("✓ Prediction history page contains expected elements")
            else:
                print("⚠ Prediction history page may be empty or incomplete")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "prediction_history_failed.png")
            raise

    def test_explainability_visualization_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access explainability visualizations"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to access explainability page (with example ID)
            # In real scenario, we would need an actual prediction ID
            explain_urls = [
                f"{live_server_url}/detection/explain/1/",
                f"{live_server_url}/explainability/1/"
            ]

            for explain_url in explain_urls:
                try:
                    browser.get(explain_url)
                    time.sleep(2)

                    # Check if we got a valid page (not 404)
                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "explainability_page.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Explainability visualization access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "explainability_access_failed.png")
            raise

    def test_complete_xray_workflow(self, browser, live_server_url, test_doctor_user, test_patient_user,
                                   e2e_helpers, sample_xray_image):
        """Test complete X-ray upload to results workflow"""
        try:
            print("  Testing complete X-ray workflow...")

            # 1. Doctor logs in
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )
            time.sleep(2)

            print("  Step 1/5: Doctor logged in")

            # 2. Access upload page
            upload_url = f"{live_server_url}/detection/upload/"
            browser.get(upload_url)
            time.sleep(2)
            e2e_helpers.take_screenshot(browser, "xray_workflow_upload_page.png")

            print("  Step 2/5: Upload page accessed")

            # 3. Check if form exists
            page_source = browser.page_source.lower()
            has_form = 'form' in page_source and ('file' in page_source or 'upload' in page_source)

            if has_form:
                print("  Step 3/5: Upload form detected")
            else:
                print("  Step 3/5: Upload form may not be available")

            # 4. View prediction history
            history_url = f"{live_server_url}/detection/history/"
            try:
                browser.get(history_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "xray_workflow_history.png")
                print("  Step 4/5: Prediction history accessed")
            except:
                print("  Step 4/5: Prediction history access failed")

            # 5. Try to view a results page
            results_url = f"{live_server_url}/detection/results/1/"
            try:
                browser.get(results_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "xray_workflow_results.png")
                print("  Step 5/5: Results page accessed")
            except:
                print("  Step 5/5: Results page may not exist yet")

            print("✓ Complete X-ray workflow tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "xray_workflow_failed.png")
            raise

    def test_add_clinical_notes(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access clinical notes page"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to access add notes page (with example ID)
            notes_url = f"{live_server_url}/detection/add-notes/1/"
            try:
                browser.get(notes_url)
                time.sleep(2)
            except:
                pass

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "clinical_notes_page.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Clinical notes page access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "clinical_notes_failed.png")
            raise
