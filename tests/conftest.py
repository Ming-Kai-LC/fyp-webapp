"""
Pytest configuration and fixtures for E2E testing
"""
import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from detection.models import UserProfile, Patient
from faker import Faker

User = get_user_model()
fake = Faker()


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    """Configure test database with migrations"""
    from django.core.management import call_command

    with django_db_blocker.unblock():
        # Run migrations to create all tables
        call_command('migrate', '--run-syncdb', verbosity=0)


@pytest.fixture(scope='function')
def browser():
    """Create a browser instance for testing"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope='function')
def live_server_url(live_server):
    """Provide the live server URL"""
    return live_server.url


@pytest.fixture
def test_patient_user(db):
    """Create a test patient user"""
    username = f"patient_{fake.user_name()}"
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password="TestPassword123!"
    )

    # UserProfile is automatically created by signal, just update it
    profile = user.profile
    profile.role = 'patient'
    profile.phone = fake.phone_number()[:15]
    profile.save()

    # Create Patient record
    dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
    from datetime import date
    age = (date.today() - dob).days // 365

    patient = Patient.objects.create(
        user=user,
        age=age,
        date_of_birth=dob,
        gender=fake.random_element(elements=('M', 'F', 'O')),
        address=fake.address()[:200],
        emergency_contact=f"{fake.name()} - {fake.phone_number()[:15]}",
        medical_history=fake.text(max_nb_chars=100),
        current_medications=fake.text(max_nb_chars=50) if fake.boolean() else ""
    )

    return {
        'user': user,
        'profile': profile,
        'patient': patient,
        'username': username,
        'password': "TestPassword123!"
    }


@pytest.fixture
def test_doctor_user(db):
    """Create a test doctor user"""
    username = f"doctor_{fake.user_name()}"
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password="TestPassword123!"
    )

    # UserProfile is automatically created by signal, just update it
    profile = user.profile
    profile.role = 'doctor'
    profile.phone = fake.phone_number()[:15]
    profile.save()

    return {
        'user': user,
        'profile': profile,
        'username': username,
        'password': "TestPassword123!"
    }


@pytest.fixture
def test_admin_user(db):
    """Create a test admin user"""
    user = User.objects.create_superuser(
        username="admin_test",
        email="admin@test.com",
        password="AdminPassword123!"
    )

    # UserProfile is automatically created by signal, just update it
    profile = user.profile
    profile.role = 'admin'
    profile.phone = fake.phone_number()[:15]
    profile.save()

    return {
        'user': user,
        'profile': profile,
        'username': "admin_test",
        'password': "AdminPassword123!"
    }


@pytest.fixture
def sample_xray_image():
    """Provide path to sample X-ray image for testing"""
    # Create a simple test image if it doesn't exist
    from PIL import Image
    import io

    test_image_path = os.path.join('tests', 'fixtures', 'test_xray.jpg')

    if not os.path.exists(test_image_path):
        # Create a simple grayscale image
        img = Image.new('L', (224, 224), color=128)
        os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
        img.save(test_image_path)

    return os.path.abspath(test_image_path)


# Helper functions for E2E tests
class E2EHelpers:
    """Helper methods for E2E testing"""

    @staticmethod
    def login(browser, live_server_url, username, password):
        """Login a user through the browser"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        browser.get(f"{live_server_url}/accounts/login/")

        username_field = browser.find_element(By.NAME, "username")
        password_field = browser.find_element(By.NAME, "password")

        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)

        submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Wait for redirect
        WebDriverWait(browser, 10).until(
            lambda driver: driver.current_url != f"{live_server_url}/accounts/login/"
        )

    @staticmethod
    def logout(browser, live_server_url):
        """Logout the current user"""
        browser.get(f"{live_server_url}/accounts/logout/")

    @staticmethod
    def wait_for_element(browser, by, value, timeout=10):
        """Wait for an element to be present"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        return WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    @staticmethod
    def wait_for_url_contains(browser, url_fragment, timeout=10):
        """Wait for URL to contain a specific fragment"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        WebDriverWait(browser, timeout).until(
            EC.url_contains(url_fragment)
        )

    @staticmethod
    def take_screenshot(browser, filename):
        """Take a screenshot for debugging"""
        screenshot_dir = os.path.join('tests', 'screenshots')
        os.makedirs(screenshot_dir, exist_ok=True)

        filepath = os.path.join(screenshot_dir, filename)
        browser.save_screenshot(filepath)
        return filepath


@pytest.fixture
def e2e_helpers():
    """Provide E2E helper methods"""
    return E2EHelpers
