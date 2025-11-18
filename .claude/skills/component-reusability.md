# Component Reusability Skill

Ensures maximum code reuse through Django's template system, mixins, and object-oriented design.

## Core Principles

1. **Component-Based Design**: Break UI into reusable components
2. **Template Inheritance**: Use Django template inheritance
3. **Include Tags**: Reuse template snippets
4. **Custom Template Tags**: Create reusable template logic
5. **Mixins**: Share functionality across views
6. **Abstract Models**: Share model fields/methods

## Template Component System

### Base Template Structure

```django
{# templates/base.html - Base layout #}
<!DOCTYPE html>
<html lang="en">
<head>
    {% block meta %}
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {% endblock %}

    <title>{% block title %}COVID-19 Detection{% endblock %}</title>

    {% block css %}
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    {% endblock %}

    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'components/navbar.html' %}

    {% include 'components/messages.html' %}

    <main class="container my-4">
        {% block content %}{% endblock %}
    </main>

    {% include 'components/footer.html' %}

    {% block js %}
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% endblock %}

    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Reusable Components

**1. Card Component**
```django
{# templates/components/card.html #}
<div class="card {{ card_class }}">
    {% if header %}
    <div class="card-header {{ header_class }}">
        {% if header_icon %}<i class="bi bi-{{ header_icon }}"></i>{% endif %}
        <h5 class="mb-0">{{ header }}</h5>
    </div>
    {% endif %}

    <div class="card-body">
        {{ content|safe }}
        {% block card_body %}{% endblock %}
    </div>

    {% if footer %}
    <div class="card-footer {{ footer_class }}">
        {{ footer|safe }}
    </div>
    {% endif %}
</div>

{# Usage #}
{% include 'components/card.html' with header="Statistics" header_icon="bar-chart" content="<p>Data here</p>" %}
```

**2. Model Comparison Table Component**
```django
{# templates/components/model_comparison_table.html #}
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Model</th>
                <th>Prediction</th>
                <th>Confidence</th>
            </tr>
        </thead>
        <tbody>
            {% for model in models %}
            <tr {% if model.is_primary %}class="table-primary"{% endif %}>
                <td>
                    {% if model.is_primary %}<strong>{% endif %}
                    {{ model.name }}
                    {% if model.is_primary %}</strong>{% endif %}
                </td>
                <td>
                    <span class="badge {{ model.prediction|diagnosis_badge_class }}">
                        {{ model.prediction }}
                    </span>
                </td>
                <td>{{ model.confidence|floatformat:2 }}%</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

{# Usage in prediction detail page #}
{% include 'components/model_comparison_table.html' with models=all_predictions %}
```

**3. Diagnosis Badge Component**
```django
{# templates/components/diagnosis_badge.html #}
{% load detection_tags %}

<span class="badge {{ diagnosis|diagnosis_badge_class }} {{ size_class }}">
    {% if show_icon %}
        <i class="bi bi-{{ diagnosis|diagnosis_icon }}"></i>
    {% endif %}
    {{ diagnosis }}
</span>

{# Usage #}
{% include 'components/diagnosis_badge.html' with diagnosis="COVID" show_icon=True size_class="fs-5" %}
```

**4. Loading Spinner Component**
```django
{# templates/components/loading.html #}
<div class="text-center py-5">
    <div class="spinner-border text-{{ color|default:'primary' }}" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
    {% if message %}
    <p class="mt-3 text-muted">{{ message }}</p>
    {% endif %}
</div>

{# Usage #}
{% include 'components/loading.html' with message="Analyzing X-ray with AI models..." color="success" %}
```

**5. Empty State Component**
```django
{# templates/components/empty_state.html #}
<div class="text-center py-5">
    <i class="bi bi-{{ icon|default:'inbox' }} display-1 text-muted"></i>
    <h4 class="mt-3">{{ title }}</h4>
    <p class="text-muted">{{ description }}</p>
    {% if action_url %}
    <a href="{{ action_url }}" class="btn btn-primary">
        <i class="bi bi-{{ action_icon|default:'plus' }}"></i> {{ action_text }}
    </a>
    {% endif %}
</div>

{# Usage #}
{% include 'components/empty_state.html' with
    icon="image"
    title="No X-rays uploaded yet"
    description="Upload an X-ray to get started with AI analysis"
    action_url="/detection/upload/"
    action_icon="cloud-upload"
    action_text="Upload X-Ray"
%}
```

**6. Stats Card Component**
```django
{# templates/components/stats_card.html #}
<div class="card text-center h-100 {{ card_class }}">
    <div class="card-body">
        <i class="bi bi-{{ icon }} display-4 text-{{ color|default:'primary' }}"></i>
        <h3 class="mt-3">{{ value }}</h3>
        <p class="text-muted mb-0">{{ label }}</p>
    </div>
</div>

{# Usage in dashboard #}
<div class="row g-4">
    <div class="col-md-3">
        {% include 'components/stats_card.html' with
            icon="bar-chart"
            value=total_predictions
            label="Total Predictions"
            color="primary"
        %}
    </div>
    <div class="col-md-3">
        {% include 'components/stats_card.html' with
            icon="shield-exclamation"
            value=covid_cases
            label="COVID Cases"
            color="danger"
        %}
    </div>
</div>
```

**7. Pagination Component**
```django
{# templates/components/pagination.html #}
{% if is_paginated %}
<nav aria-label="Page navigation">
    <ul class="pagination justify-content-center">
        {% if page_obj.has_previous %}
        <li class="page-item">
            <a class="page-link" href="?page=1">First</a>
        </li>
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.previous_page_number }}">
                <i class="bi bi-chevron-left"></i> Previous
            </a>
        </li>
        {% endif %}

        <li class="page-item active">
            <span class="page-link">
                Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
            </span>
        </li>

        {% if page_obj.has_next %}
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.next_page_number }}">
                Next <i class="bi bi-chevron-right"></i>
            </a>
        </li>
        <li class="page-item">
            <a class="page-link" href="?page={{ page_obj.paginator.num_pages }}">Last</a>
        </li>
        {% endif %}
    </ul>
</nav>
{% endif %}

{# Usage in any list view #}
{% include 'components/pagination.html' %}
```

## Custom Template Tags (Reusable Logic)

```python
# detection/templatetags/detection_tags.py
from django import template
from typing import Dict, List, Any

register = template.Library()


@register.filter
def diagnosis_badge_class(diagnosis: str) -> str:
    """Return Bootstrap badge class for diagnosis"""
    mapping = {
        'COVID': 'bg-danger',
        'Normal': 'bg-success',
        'Viral Pneumonia': 'bg-warning text-dark',
        'Lung Opacity': 'bg-info',
    }
    return mapping.get(diagnosis, 'bg-secondary')


@register.filter
def diagnosis_icon(diagnosis: str) -> str:
    """Return Bootstrap icon for diagnosis"""
    mapping = {
        'COVID': 'shield-exclamation',
        'Normal': 'check-circle',
        'Viral Pneumonia': 'exclamation-triangle',
        'Lung Opacity': 'info-circle',
    }
    return mapping.get(diagnosis, 'question-circle')


@register.filter
def confidence_color(confidence: float) -> str:
    """Return color class based on confidence level"""
    if confidence >= 90:
        return 'success'
    elif confidence >= 75:
        return 'warning'
    else:
        return 'danger'


@register.inclusion_tag('components/model_comparison_table.html')
def model_comparison(prediction) -> Dict[str, Any]:
    """Render model comparison table"""
    return {
        'models': prediction.get_all_predictions(),
        'best_model': prediction.get_best_model(),
    }


@register.inclusion_tag('components/prediction_card.html')
def prediction_card(prediction, show_actions: bool = True) -> Dict[str, Any]:
    """Render prediction result card"""
    return {
        'prediction': prediction,
        'show_actions': show_actions,
        'is_high_confidence': prediction.is_high_confidence(),
    }


@register.simple_tag
def active_nav(request, url_name: str) -> str:
    """Return 'active' if current page matches url_name"""
    from django.urls import reverse
    current_url = request.path
    target_url = reverse(url_name)
    return 'active' if current_url == target_url else ''


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs) -> str:
    """
    Update URL query parameters while preserving existing ones.
    Useful for pagination with filters.

    Usage:
        <a href="?{% query_transform page=2 %}">Next</a>
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()


# Usage in templates
```django
{% load detection_tags %}

<!-- Diagnosis badge with custom filter -->
<span class="badge {{ prediction.final_diagnosis|diagnosis_badge_class }}">
    <i class="bi bi-{{ prediction.final_diagnosis|diagnosis_icon }}"></i>
    {{ prediction.final_diagnosis }}
</span>

<!-- Model comparison table with inclusion tag -->
{% model_comparison prediction %}

<!-- Active navigation highlighting -->
<li class="nav-item">
    <a class="nav-link {% active_nav request 'detection:dashboard' %}" href="{% url 'detection:dashboard' %}">
        Dashboard
    </a>
</li>

<!-- Pagination with query params -->
<a href="?{% query_transform page=page_obj.next_page_number %}">Next</a>
```

## Reusable View Mixins

```python
# detection/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from typing import Any

class RoleRequiredMixin(LoginRequiredMixin):
    """Base mixin for role-based access"""
    required_role: str = None

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "User profile not found.")
            return redirect('home')

        if self.required_role and request.user.profile.role != self.required_role:
            messages.error(request, f"Access denied. {self.required_role.title()}s only.")
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class DoctorRequiredMixin(RoleRequiredMixin):
    required_role = 'doctor'


class PatientRequiredMixin(RoleRequiredMixin):
    required_role = 'patient'


class PageTitleMixin:
    """Add page title to context"""
    page_title: str = ""

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class FilterMixin:
    """Add filtering capability to list views"""
    filter_fields: list = []

    def get_queryset(self):
        qs = super().get_queryset()

        for field in self.filter_fields:
            value = self.request.GET.get(field)
            if value:
                qs = qs.filter(**{field: value})

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = {
            field: self.request.GET.get(field, '')
            for field in self.filter_fields
        }
        return context


# Usage: Combine multiple mixins
class PredictionListView(DoctorRequiredMixin, PageTitleMixin, FilterMixin, ListView):
    model = Prediction
    template_name = 'detection/prediction_list.html'
    page_title = "Prediction History"
    filter_fields = ['final_diagnosis', 'is_validated']
    paginate_by = 25
```

## Reusable Form Widgets

```python
# detection/widgets.py
from django import forms

class BootstrapFileInput(forms.FileInput):
    """Bootstrap 5 styled file input"""
    template_name = 'widgets/bootstrap_file_input.html'

    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class BootstrapTextarea(forms.Textarea):
    """Bootstrap 5 styled textarea"""
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control', 'rows': 3}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class BootstrapSelect(forms.Select):
    """Bootstrap 5 styled select"""
    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-select'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


# Usage in forms
class XRayUploadForm(forms.ModelForm):
    class Meta:
        model = XRayImage
        fields = ['patient', 'original_image', 'notes']
        widgets = {
            'patient': BootstrapSelect(),
            'original_image': BootstrapFileInput(attrs={'accept': 'image/*'}),
            'notes': BootstrapTextarea(attrs={'placeholder': 'Add notes...'}),
        }
```

## Abstract Base Models

```python
# detection/models.py
from django.db import models

class TimeStampedModel(models.Model):
    """Abstract model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UserTrackingModel(TimeStampedModel):
    """Abstract model with user tracking"""
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True


# Usage: Inherit from base models
class Prediction(TimeStampedModel):
    """Automatically has created_at and updated_at"""
    pass

class XRayImage(UserTrackingModel):
    """Automatically has created_at, updated_at, created_by, updated_by"""
    pass
```

## Component Library Structure

```
templates/
├── components/              # Reusable components
│   ├── card.html
│   ├── diagnosis_badge.html
│   ├── empty_state.html
│   ├── footer.html
│   ├── loading.html
│   ├── messages.html
│   ├── model_comparison_table.html
│   ├── navbar.html
│   ├── pagination.html
│   ├── prediction_card.html
│   └── stats_card.html
├── layouts/                 # Page layouts
│   ├── base.html
│   ├── dashboard_base.html
│   └── auth_base.html
└── pages/                   # Full pages (inherit from layouts)
    └── detection/
        ├── upload.html
        ├── results.html
        └── history.html
```

## Reusability Checklist

When creating new features:

- ✅ Can this be a reusable component?
- ✅ Should this logic be in a mixin?
- ✅ Can this template be split into includes?
- ✅ Should this be a custom template tag?
- ✅ Is there an existing component I can reuse?
- ✅ Can this model inherit from a base class?
- ✅ Can this form widget be made generic?
- ✅ Is this business logic better in a service?

## Benefits of Component Reusability

1. **Consistency**: Same look/behavior everywhere
2. **Maintainability**: Fix once, update everywhere
3. **Development Speed**: Build faster with existing components
4. **Testing**: Test once, reuse everywhere
5. **Code Quality**: Less duplication, cleaner code

## Auto-Apply This Skill When:
- Creating new templates
- Building new features
- Noticing repeated code
- Adding new views
- Designing UI components
- Refactoring existing code
