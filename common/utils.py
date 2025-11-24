"""
Common utility functions and helpers for the COVID-19 Detection application.

These functions provide reusable logic for validation, formatting, file handling,
and other common operations to maintain DRY principles.

Usage:
    from common.utils import validate_phone, format_file_size, generate_unique_filename
"""

import os
import uuid
import re
from typing import Optional, Tuple, List
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime, timedelta


# ==============================================================================
# VALIDATION UTILITIES
# ==============================================================================

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (Malaysian format).

    Args:
        phone: Phone number string

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If phone number is invalid

    Example:
        validate_phone("+60123456789")  # Valid
        validate_phone("0123456789")     # Valid
    """
    if not phone:
        raise ValidationError("Phone number is required")

    # Remove spaces and dashes
    cleaned = re.sub(r'[\s-]', '', phone)

    # Malaysian phone patterns
    patterns = [
        r'^\+60\d{9,10}$',  # +60123456789
        r'^0\d{9,10}$',     # 0123456789
        r'^60\d{9,10}$',    # 60123456789
    ]

    if not any(re.match(pattern, cleaned) for pattern in patterns):
        raise ValidationError(
            "Invalid phone number format. Use +60123456789 or 0123456789"
        )

    return True


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address string

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If email is invalid
    """
    try:
        django_validate_email(email)
        return True
    except ValidationError:
        raise ValidationError("Invalid email format")


def validate_nric(nric: str) -> bool:
    """
    Validate Malaysian IC/NRIC number format.

    Args:
        nric: NRIC number (e.g., "901231-01-1234")

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If NRIC is invalid
    """
    if not nric:
        raise ValidationError("NRIC is required")

    # Remove dashes
    cleaned = nric.replace('-', '')

    # NRIC format: YYMMDD-PB-###G (12 digits)
    if not re.match(r'^\d{12}$', cleaned):
        raise ValidationError(
            "Invalid NRIC format. Use YYMMDD-PB-###G (e.g., 901231-01-1234)"
        )

    # Extract date parts
    yy = cleaned[:2]
    mm = cleaned[2:4]
    dd = cleaned[4:6]

    # Validate month and day
    if not (1 <= int(mm) <= 12):
        raise ValidationError("Invalid month in NRIC")

    if not (1 <= int(dd) <= 31):
        raise ValidationError("Invalid day in NRIC")

    return True


def validate_age(date_of_birth: datetime, min_age: int = 0, max_age: int = 120) -> bool:
    """
    Validate age based on date of birth.

    Args:
        date_of_birth: Date of birth
        min_age: Minimum allowed age
        max_age: Maximum allowed age

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If age is out of range
    """
    if not date_of_birth:
        raise ValidationError("Date of birth is required")

    today = timezone.now().date()
    age = (today - date_of_birth).days // 365

    if age < min_age:
        raise ValidationError(f"Age must be at least {min_age} years")

    if age > max_age:
        raise ValidationError(f"Age must be less than {max_age} years")

    return True


# ==============================================================================
# FILE UTILITIES
# ==============================================================================

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension.

    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If extension not allowed
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )

    return True


def validate_file_size(file, max_size_mb: int = 10) -> bool:
    """
    Validate file size.

    Args:
        file: Uploaded file object
        max_size_mb: Maximum allowed size in MB

    Returns:
        bool: True if valid

    Raises:
        ValidationError: If file too large
    """
    max_size = max_size_mb * 1024 * 1024  # Convert to bytes

    if file.size > max_size:
        raise ValidationError(
            f"File too large. Maximum size: {max_size_mb}MB. Your file: {format_file_size(file.size)}"
        )

    return True


def validate_image_file(file, max_size_mb: int = 10) -> bool:
    """
    Validate image file (extension and size).

    Args:
        file: Uploaded file object
        max_size_mb: Maximum allowed size in MB

    Returns:
        bool: True if valid

    Example:
        validate_image_file(request.FILES['xray'], max_size_mb=10)
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    validate_file_extension(file.name, allowed_extensions)
    validate_file_size(file, max_size_mb)
    return True


def generate_unique_filename(filename: str, prefix: str = '') -> str:
    """
    Generate unique filename with UUID to avoid conflicts.

    Args:
        filename: Original filename
        prefix: Optional prefix for the filename

    Returns:
        str: Unique filename

    Example:
        generate_unique_filename('xray.png', 'patient')
        # Returns: 'patient_abc123de-f456-7890-gh12-ijk345lmn678.png'
    """
    ext = os.path.splitext(filename)[1]
    unique_id = uuid.uuid4().hex[:12]

    if prefix:
        return f"{slugify(prefix)}_{unique_id}{ext}"

    return f"{unique_id}{ext}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        str: Formatted size (e.g., "1.5 MB")

    Example:
        format_file_size(1572864)  # Returns: "1.5 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.1f} PB"


# ==============================================================================
# FORMATTING UTILITIES
# ==============================================================================

def format_phone_display(phone: str) -> str:
    """
    Format phone number for display.

    Args:
        phone: Phone number string

    Returns:
        str: Formatted phone number

    Example:
        format_phone_display("+60123456789")  # Returns: "+60 12-345-6789"
    """
    if not phone:
        return ""

    # Remove non-numeric characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')

    # Format Malaysian numbers
    if cleaned.startswith('+60'):
        country = cleaned[:3]
        rest = cleaned[3:]
        if len(rest) >= 9:
            return f"{country} {rest[:2]}-{rest[2:5]}-{rest[5:]}"

    if cleaned.startswith('0'):
        return f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"

    return phone


def format_nric_display(nric: str) -> str:
    """
    Format NRIC for display.

    Args:
        nric: NRIC number

    Returns:
        str: Formatted NRIC

    Example:
        format_nric_display("901231011234")  # Returns: "901231-01-1234"
    """
    if not nric:
        return ""

    cleaned = nric.replace('-', '')
    if len(cleaned) == 12:
        return f"{cleaned[:6]}-{cleaned[6:8]}-{cleaned[8:]}"

    return nric


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: String to append (default: '...')

    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length].rsplit(' ', 1)[0] + suffix


def slugify_filename(filename: str) -> str:
    """
    Create URL-safe slug from filename.

    Args:
        filename: Original filename

    Returns:
        str: Slugified filename

    Example:
        slugify_filename("Patient Report 2024.pdf")
        # Returns: "patient-report-2024.pdf"
    """
    name, ext = os.path.splitext(filename)
    return slugify(name) + ext


# ==============================================================================
# DATE/TIME UTILITIES
# ==============================================================================

def calculate_age(date_of_birth: datetime) -> int:
    """
    Calculate age from date of birth.

    Args:
        date_of_birth: Date of birth

    Returns:
        int: Age in years
    """
    if not date_of_birth:
        return 0

    today = timezone.now().date()
    return (today - date_of_birth).days // 365


def is_business_hours(dt: datetime, start_hour: int = 9, end_hour: int = 17) -> bool:
    """
    Check if datetime is within business hours.

    Args:
        dt: Datetime to check
        start_hour: Business start hour (default: 9 AM)
        end_hour: Business end hour (default: 5 PM)

    Returns:
        bool: True if within business hours
    """
    if not dt:
        return False

    return start_hour <= dt.hour < end_hour


def is_weekend(dt: datetime) -> bool:
    """
    Check if datetime is on weekend (Saturday or Sunday).

    Args:
        dt: Datetime to check

    Returns:
        bool: True if weekend
    """
    if not dt:
        return False

    return dt.weekday() in [5, 6]  # 5=Saturday, 6=Sunday


def next_business_day(dt: datetime = None) -> datetime:
    """
    Get next business day (skip weekends).

    Args:
        dt: Starting datetime (default: now)

    Returns:
        datetime: Next business day
    """
    if dt is None:
        dt = timezone.now()

    next_day = dt + timedelta(days=1)

    while is_weekend(next_day):
        next_day += timedelta(days=1)

    return next_day


def time_since(dt: datetime) -> str:
    """
    Get human-readable time since datetime.

    Args:
        dt: Past datetime

    Returns:
        str: Human-readable time (e.g., "2 hours ago")
    """
    if not dt:
        return ""

    now = timezone.now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years > 1 else ''} ago"


# ==============================================================================
# SECURITY UTILITIES
# ==============================================================================

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)

    # Remove potentially dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Prevent empty filenames
    if not filename:
        filename = 'unnamed_file'

    return filename


def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = '*') -> str:
    """
    Mask sensitive data (e.g., NRIC, phone numbers).

    Args:
        data: Sensitive data string
        visible_chars: Number of characters to keep visible
        mask_char: Character to use for masking

    Returns:
        str: Masked string

    Example:
        mask_sensitive_data("901231-01-1234", 4)  # Returns: "901231-**-****"
        mask_sensitive_data("+60123456789", 4)    # Returns: "+60*****6789"
    """
    if not data or len(data) <= visible_chars:
        return data

    visible_start = visible_chars // 2
    visible_end = visible_chars - visible_start

    masked = (
        data[:visible_start] +
        mask_char * (len(data) - visible_chars) +
        data[-visible_end:] if visible_end > 0 else ''
    )

    return masked


# ==============================================================================
# DATA HELPERS
# ==============================================================================

def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, avoiding division by zero.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        float: Result of division or default
    """
    try:
        return numerator / denominator
    except (ZeroDivisionError, TypeError):
        return default


def percentage_of(part: float, whole: float, decimals: int = 1) -> str:
    """
    Calculate percentage of part to whole.

    Args:
        part: Part value
        whole: Whole value
        decimals: Number of decimal places

    Returns:
        str: Percentage string (e.g., "75.5%")
    """
    if not whole or whole == 0:
        return "0.0%"

    percentage = (part / whole) * 100
    return f"{percentage:.{decimals}f}%"


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value

    Returns:
        float: Clamped value
    """
    return max(min_value, min(value, max_value))
