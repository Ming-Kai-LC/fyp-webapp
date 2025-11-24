"""
Reusable template tags and filters for consistent UI/UX across the application.

These tags provide common functionality like status badges, pagination,
formatting, and UI components without repeating code in templates.

Usage:
    {% load common_tags %}
    {% status_badge prediction.status %}
    {% render_pagination page_obj %}
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json

register = template.Library()


# ==============================================================================
# STATUS BADGES
# ==============================================================================

@register.simple_tag
def status_badge(status, custom_classes=''):
    """
    Render a Bootstrap badge for a given status.

    Args:
        status: The status text
        custom_classes: Additional CSS classes

    Usage:
        {% status_badge prediction.status %}
        {% status_badge appointment.status "ms-2" %}
    """
    # Status to Bootstrap color mapping
    status_colors = {
        # General statuses
        'pending': 'warning',
        'processing': 'info',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'secondary',

        # Appointment statuses
        'scheduled': 'primary',
        'confirmed': 'success',
        'no_show': 'danger',

        # Prediction statuses
        'covid': 'danger',
        'normal': 'success',
        'viral_pneumonia': 'warning',
        'lung_opacity': 'info',
    }

    status_lower = str(status).lower().replace(' ', '_')
    color = status_colors.get(status_lower, 'secondary')

    return format_html(
        '<span class="badge bg-{} {}">{}</span>',
        color,
        custom_classes,
        status
    )


@register.simple_tag
def diagnosis_badge(diagnosis):
    """
    Render a diagnosis-specific badge with icon.

    Usage:
        {% diagnosis_badge prediction.diagnosis %}
    """
    diagnosis_config = {
        'COVID': {'icon': 'bi-virus', 'color': 'danger'},
        'Normal': {'icon': 'bi-check-circle', 'color': 'success'},
        'Viral Pneumonia': {'icon': 'bi-lungs', 'color': 'warning'},
        'Lung Opacity': {'icon': 'bi-cloud', 'color': 'info'},
    }

    config = diagnosis_config.get(diagnosis, {'icon': 'bi-question-circle', 'color': 'secondary'})

    return format_html(
        '<span class="badge bg-{}"><i class="{}"></i> {}</span>',
        config['color'],
        config['icon'],
        diagnosis
    )


@register.simple_tag
def confidence_badge(confidence):
    """
    Render a confidence percentage badge with appropriate color.

    Args:
        confidence: Float between 0 and 1 or percentage string

    Usage:
        {% confidence_badge prediction.confidence %}
    """
    try:
        # Convert to float if it's a string percentage
        if isinstance(confidence, str):
            confidence = float(confidence.strip('%')) / 100

        percentage = float(confidence) * 100

        # Color based on confidence level
        if percentage >= 90:
            color = 'success'
        elif percentage >= 75:
            color = 'info'
        elif percentage >= 60:
            color = 'warning'
        else:
            color = 'danger'

        return format_html(
            '<span class="badge bg-{}">{:.1f}%</span>',
            color,
            percentage
        )
    except (ValueError, TypeError):
        return format_html('<span class="badge bg-secondary">N/A</span>')


# ==============================================================================
# PAGINATION
# ==============================================================================

@register.inclusion_tag('components/pagination.html')
def render_pagination(page_obj, page_range=5):
    """
    Render a Bootstrap 5 pagination component.

    Args:
        page_obj: Django paginator page object
        page_range: Number of page numbers to show

    Usage:
        {% render_pagination page_obj %}
    """
    if not page_obj:
        return {'page_obj': None}

    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages

    # Calculate page range to display
    start_page = max(1, current_page - page_range // 2)
    end_page = min(total_pages, start_page + page_range - 1)

    # Adjust start if we're near the end
    if end_page - start_page < page_range - 1:
        start_page = max(1, end_page - page_range + 1)

    page_numbers = range(start_page, end_page + 1)

    return {
        'page_obj': page_obj,
        'page_numbers': page_numbers,
        'show_first': start_page > 1,
        'show_last': end_page < total_pages,
    }


# ==============================================================================
# FORMATTING FILTERS
# ==============================================================================

@register.filter
def percentage(value, decimals=1):
    """
    Format a float as a percentage.

    Usage:
        {{ 0.856 | percentage }}  -> 85.6%
        {{ 0.856 | percentage:2 }}  -> 85.60%
    """
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


@register.filter
def format_phone(value):
    """
    Format a phone number.

    Usage:
        {{ "+60123456789" | format_phone }}  -> +60 12-345-6789
    """
    if not value:
        return ""

    # Remove non-numeric characters except +
    cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '+')

    # Format Malaysian phone numbers (+60)
    if cleaned.startswith('+60'):
        country = cleaned[:3]
        rest = cleaned[3:]
        if len(rest) >= 9:
            return f"{country} {rest[:2]}-{rest[2:5]}-{rest[5:]}"

    return value


@register.filter
def format_date(value, format_string='%Y-%m-%d'):
    """
    Format a datetime object.

    Usage:
        {{ appointment.scheduled_date | format_date:"%d %b %Y" }}
    """
    try:
        return value.strftime(format_string)
    except (AttributeError, ValueError):
        return value


@register.filter
def format_datetime(value):
    """
    Format a datetime in user-friendly format.

    Usage:
        {{ prediction.created_at | format_datetime }}
    """
    try:
        return value.strftime('%d %b %Y, %I:%M %p')
    except (AttributeError, ValueError):
        return value


@register.filter
def truncate_chars(value, length=50):
    """
    Truncate text to specified length with ellipsis.

    Usage:
        {{ description | truncate_chars:100 }}
    """
    if not value:
        return ""

    text = str(value)
    if len(text) <= length:
        return text

    return text[:length].rsplit(' ', 1)[0] + '...'


# ==============================================================================
# PERMISSION CHECKS
# ==============================================================================

@register.simple_tag
def user_can(user, action, obj=None):
    """
    Check if user has permission for an action.

    Args:
        user: User object
        action: 'create', 'update', 'delete', 'view'
        obj: Optional object to check permissions on

    Usage:
        {% user_can request.user 'create' appointment as can_create %}
        {% if can_create %}
            <a href="...">Create</a>
        {% endif %}
    """
    if not user or not user.is_authenticated:
        return False

    profile = getattr(user, 'profile', None)
    if not profile:
        return False

    # Admin can do everything
    if profile.is_admin():
        return True

    # Staff permissions
    if profile.is_staff():
        if action in ['view', 'create', 'update']:
            return True
        if action == 'delete' and obj:
            # Staff can only delete own pending items
            return getattr(obj, 'created_by', None) == user and getattr(obj, 'status', None) == 'pending'
        return False

    # Patient permissions
    if profile.is_patient():
        if action == 'view' and obj:
            # Patients can only view their own data
            return getattr(obj, 'user', None) == user or getattr(obj, 'patient.user', None) == user
        if action == 'update' and obj:
            # Patients can update their own profile
            return getattr(obj, 'user', None) == user
        return False

    return False


# ==============================================================================
# UI HELPERS
# ==============================================================================

@register.simple_tag
def alert_box(message, alert_type='info', dismissible=True):
    """
    Render a Bootstrap alert box.

    Args:
        message: Alert message
        alert_type: 'primary', 'success', 'danger', 'warning', 'info'
        dismissible: Whether to show dismiss button

    Usage:
        {% alert_box "Success!" "success" %}
    """
    dismiss_btn = ''
    if dismissible:
        dismiss_btn = '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>'

    dismissible_class = ' alert-dismissible fade show' if dismissible else ''

    return format_html(
        '<div class="alert alert-{}{}" role="alert">{}{}</div>',
        alert_type,
        dismissible_class,
        message,
        mark_safe(dismiss_btn)
    )


@register.simple_tag
def loading_spinner(text='Loading...'):
    """
    Render a loading spinner.

    Usage:
        {% loading_spinner "Processing..." %}
    """
    return format_html(
        '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">{}</span></div><p class="mt-2">{}</p></div>',
        text,
        text
    )


@register.simple_tag
def icon(name, size='', color=''):
    """
    Render a Bootstrap Icon.

    Args:
        name: Icon name (e.g., 'check-circle', 'x-circle')
        size: Font size class (e.g., 'fs-4')
        color: Text color class (e.g., 'text-success')

    Usage:
        {% icon 'check-circle' 'fs-4' 'text-success' %}
    """
    return format_html(
        '<i class="bi bi-{} {} {}"></i>',
        name,
        size,
        color
    )


@register.simple_tag
def card(title='', body='', footer='', header_class='', body_class='', footer_class=''):
    """
    Render a Bootstrap card component.

    Usage:
        {% card title="Patient Info" body="Content here" %}
    """
    card_html = '<div class="card">'

    if title:
        card_html += f'<div class="card-header {header_class}">{title}</div>'

    if body:
        card_html += f'<div class="card-body {body_class}">{body}</div>'

    if footer:
        card_html += f'<div class="card-footer {footer_class}">{footer}</div>'

    card_html += '</div>'

    return mark_safe(card_html)


# ==============================================================================
# DATA HELPERS
# ==============================================================================

@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary in template.

    Usage:
        {{ stats|get_item:"total_patients" }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)


@register.filter
def json_dumps(value):
    """
    Convert Python object to JSON string.

    Usage:
        <script>
            const data = {{ stats|json_dumps }};
        </script>
    """
    try:
        return mark_safe(json.dumps(value))
    except (TypeError, ValueError):
        return '{}'


@register.simple_tag
def query_transform(request, **kwargs):
    """
    Transform query parameters for pagination and filtering.

    Usage:
        <a href="?{% query_transform request page=2 %}">Next</a>
    """
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            updated[k] = v
        elif k in updated:
            del updated[k]

    return updated.urlencode()


# ==============================================================================
# MATH HELPERS
# ==============================================================================

@register.filter
def multiply(value, arg):
    """
    Multiply two numbers.

    Usage:
        {{ confidence|multiply:100 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    Divide two numbers.

    Usage:
        {{ total|divide:count }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def subtract(value, arg):
    """
    Subtract two numbers.

    Usage:
        {{ total|subtract:discount }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def add_class(field, css_class):
    """
    Add CSS class to form field.

    Usage:
        {{ form.field|add_class:"custom-class" }}
    """
    return field.as_widget(attrs={"class": css_class})
