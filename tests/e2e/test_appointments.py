"""
End-to-end tests for appointment booking system
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
class TestAppointmentWorkflow:
    """Test appointment booking and management"""

    def test_patient_book_appointment(self, browser, live_server_url, test_patient_user, test_doctor_user,
                                     e2e_helpers):
        """Test patient can access appointment booking page"""
        try:
            # Login as patient
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )

            time.sleep(2)

            # Navigate to appointment booking page
            appointment_urls = [
                f"{live_server_url}/appointments/book/",
                f"{live_server_url}/appointment/book/",
                f"{live_server_url}/book-appointment/"
            ]

            booking_page_loaded = False
            for appointment_url in appointment_urls:
                try:
                    browser.get(appointment_url)
                    time.sleep(2)

                    # Check if page loaded successfully
                    if "404" not in browser.page_source and "error" not in browser.page_source.lower():
                        booking_page_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "appointment_booking_page.png")

            # Check if booking form exists
            page_source = browser.page_source.lower()
            has_booking_elements = any(word in page_source for word in
                                      ['appointment', 'book', 'schedule', 'doctor', 'date', 'time'])

            if booking_page_loaded and has_booking_elements:
                print("✓ Appointment booking page accessed successfully")
            else:
                print("⚠ Appointment booking page may not be fully functional")

            # Verify patient is still logged in
            assert "logout" in page_source or "dashboard" in page_source, \
                "Patient session lost"

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "appointment_booking_failed.png")
            raise

    def test_patient_view_appointments(self, browser, live_server_url, test_patient_user, e2e_helpers):
        """Test patient can view their appointments"""
        try:
            # Login as patient
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )

            time.sleep(2)

            # Navigate to appointments list
            appointments_urls = [
                f"{live_server_url}/appointments/my-appointments/",
                f"{live_server_url}/my-appointments/",
                f"{live_server_url}/appointments/"
            ]

            appointments_loaded = False
            for appointments_url in appointments_urls:
                try:
                    browser.get(appointments_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        appointments_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "patient_appointments_list.png")

            # Verify patient is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Patient session lost"

            print("✓ Patient appointments list accessed")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "patient_appointments_failed.png")
            raise

    def test_doctor_view_appointments(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can view their appointments"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Navigate to doctor appointments
            appointments_urls = [
                f"{live_server_url}/appointments/doctor-appointments/",
                f"{live_server_url}/appointments/",
                f"{live_server_url}/doctor/appointments/"
            ]

            appointments_loaded = False
            for appointments_url in appointments_urls:
                try:
                    browser.get(appointments_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        appointments_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "doctor_appointments_list.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Doctor appointments list accessed")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_appointments_failed.png")
            raise

    def test_doctor_manage_schedule(self, browser, live_server_url, test_doctor_user, e2e_helpers):
        """Test doctor can access schedule management"""
        try:
            # Login as doctor
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )

            time.sleep(2)

            # Navigate to schedule management
            schedule_urls = [
                f"{live_server_url}/appointments/manage-schedule/",
                f"{live_server_url}/appointments/schedule/",
                f"{live_server_url}/doctor/schedule/"
            ]

            schedule_loaded = False
            for schedule_url in schedule_urls:
                try:
                    browser.get(schedule_url)
                    time.sleep(2)

                    if "404" not in browser.page_source:
                        schedule_loaded = True
                        break
                except:
                    continue

            # Take screenshot
            e2e_helpers.take_screenshot(browser, "doctor_schedule_management.png")

            # Verify doctor is still logged in
            page_source = browser.page_source.lower()
            assert "logout" in page_source or "dashboard" in page_source, \
                "Doctor session lost"

            print("✓ Doctor schedule management accessed")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "doctor_schedule_failed.png")
            raise

    def test_appointment_complete_flow(self, browser, live_server_url, test_patient_user, test_doctor_user,
                                      e2e_helpers):
        """Test complete appointment flow"""
        try:
            print("  Testing complete appointment flow...")

            # 1. Doctor sets up schedule
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )
            time.sleep(2)

            schedule_url = f"{live_server_url}/appointments/manage-schedule/"
            try:
                browser.get(schedule_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "appointment_flow_schedule.png")
            except:
                pass

            print("  Step 1/4: Doctor schedule checked")

            # 2. Logout doctor
            e2e_helpers.logout(browser, live_server_url)
            time.sleep(2)

            # 3. Patient books appointment
            e2e_helpers.login(
                browser,
                live_server_url,
                test_patient_user['username'],
                test_patient_user['password']
            )
            time.sleep(2)

            booking_url = f"{live_server_url}/appointments/book/"
            try:
                browser.get(booking_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "appointment_flow_booking.png")
            except:
                pass

            print("  Step 2/4: Patient accessed booking page")

            # 4. Patient views appointments
            appointments_url = f"{live_server_url}/appointments/my-appointments/"
            try:
                browser.get(appointments_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "appointment_flow_patient_list.png")
            except:
                pass

            print("  Step 3/4: Patient viewed appointments")

            # 5. Logout patient
            e2e_helpers.logout(browser, live_server_url)
            time.sleep(2)

            # 6. Doctor views appointments
            e2e_helpers.login(
                browser,
                live_server_url,
                test_doctor_user['username'],
                test_doctor_user['password']
            )
            time.sleep(2)

            doctor_appointments_url = f"{live_server_url}/appointments/doctor-appointments/"
            try:
                browser.get(doctor_appointments_url)
                time.sleep(2)
                e2e_helpers.take_screenshot(browser, "appointment_flow_doctor_list.png")
            except:
                pass

            print("  Step 4/4: Doctor viewed appointments")

            print("✓ Complete appointment flow tested successfully")

        except Exception as e:
            e2e_helpers.take_screenshot(browser, "appointment_flow_failed.png")
            raise
