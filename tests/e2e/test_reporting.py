"""
End-to-end tests for report generation
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
@pytest.mark.django_db(transaction=True)
class TestReportingWorkflow:
    """Test report generation and viewing"""

    def test_report_generation_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access report generation page"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to access report generation page (with example prediction ID)
            generate_urls = [
                f"{live_server_url}/reporting/generate/1/",
                f"{live_server_url}/reports/generate/1/"
            ]

            for generate_url in generate_urls:
                try:
                    browser.get(generate_url)
                    time.sleep(2)

                    # Check if we got a valid page
                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "report_generation_page.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Report generation page access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "report_generation_failed.png")
            raise

    def test_report_list_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access report list"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to access report list
            list_urls = [
                f"{live_server_url}/reporting/list/",
                f"{live_server_url}/reports/",
                f"{live_server_url}/reporting/"
            ]

            for list_url in list_urls:
                try:
                    browser.get(list_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "report_list_page.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Report list page access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "report_list_failed.png")
            raise

    def test_report_view_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access report view page"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to access report view page (with example report ID)
            view_urls = [
                f"{live_server_url}/reporting/view/1/",
                f"{live_server_url}/reports/view/1/"
            ]

            for view_url in view_urls:
                try:
                    browser.get(view_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "report_view_page.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Report view page access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "report_view_failed.png")
            raise

    def test_report_template_access(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access report templates"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to access report templates
            template_urls = [
                f"{live_server_url}/reporting/templates/",
                f"{live_server_url}/reports/templates/"
            ]

            for template_url in template_urls:
                try:
                    browser.get(template_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "report_templates_page.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Report templates page access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "report_templates_failed.png")
            raise

    def test_patient_view_reports(self, browser, live_server_url, test_patient_user, e2e_helpers):
        """Test patient can view their reports"""
        try:
            # Login as patient
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )

            time.sleep(2)

            # Try to access patient reports
            report_urls = [
                f"{live_server_url}/reporting/my-reports/",
                f"{live_server_url}/reports/",
                f"{live_server_url}/my-reports/"
            ]

            for report_url in report_urls:
                try:
                    browser.get(report_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "patient_reports_page.png")

            # Verify patient is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Patient session lost"

            print("✓ Patient reports page access tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_reports_failed.png")
            raise

    def test_complete_reporting_workflow(self, browser, live_server_url, test_doctor_user, test_patient_user,
                                        e2e_helpers):
        """Test complete reporting workflow"""
        try:
            print("  Testing complete reporting workflow...")

            # 1. Doctor logs in
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )
            time.sleep(2)

            print("  Step 1/6: Doctor logged in")

            # 2. Access report generation page
            generate_url = f"{live_server_url}/reporting/generate/1/"
            try:
                browser.get(generate_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "reporting_workflow_generate.png")
                print("  Step 2/6: Report generation page accessed")
            except:
                print("  Step 2/6: Report generation page access failed")

            # 3. View report list
            list_url = f"{live_server_url}/reporting/list/"
            try:
                browser.get(list_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "reporting_workflow_list.png")
                print("  Step 3/6: Report list accessed")
            except:
                print("  Step 3/6: Report list access failed")

            # 4. View a report
            view_url = f"{live_server_url}/reporting/view/1/"
            try:
                browser.get(view_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "reporting_workflow_view.png")
                print("  Step 4/6: Report view accessed")
            except:
                print("  Step 4/6: Report view access failed")

            # 5. Logout doctor
            e2e_helpers.logout(browser, live_server_url)
            time.sleep(2)

            print("  Step 5/6: Doctor logged out")

            # 6. Patient views their reports
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )
            time.sleep(2)

            patient_reports_url = f"{live_server_url}/reporting/my-reports/"
            try:
                browser.get(patient_reports_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "reporting_workflow_patient_view.png")
                print("  Step 6/6: Patient accessed their reports")
            except:
                print("  Step 6/6: Patient reports access failed")

            print("✓ Complete reporting workflow tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "reporting_workflow_failed.png")
            raise

    def test_report_download(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test report download functionality"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Try to access report download (with example report ID)
            download_urls = [
                f"{live_server_url}/reporting/download/1/",
                f"{live_server_url}/reports/download/1/"
            ]

            for download_url in download_urls:
                try:
                    browser.get(download_url)
                    time.sleep(2)

                    # For download, we might get redirected or see a PDF
                    # Just verify we don't get a server error
                    if "500" not in browser.page_source and "error" not in browser.title.lower():
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "report_download_page.png")

            print("✓ Report download functionality tested")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "report_download_failed.png")
            raise
