# UI/UX Design System
## COVID-19 Detection Web Application

**Version:** 1.0.0
**Last Updated:** 2025-11-22
**Framework:** Bootstrap 5.3

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components](#components)
6. [Forms](#forms)
7. [Icons](#icons)
8. [Responsive Design](#responsive-design)
9. [Accessibility](#accessibility)
10. [Usage Examples](#usage-examples)

---

## Design Philosophy

### Core Principles

1. **Consistency**: Same UI patterns across all modules for predictable user experience
2. **Clarity**: Medical data presented clearly with appropriate visual hierarchy
3. **Accessibility**: WCAG 2.1 AA compliant for all users
4. **Responsiveness**: Mobile-first design that works on all devices
5. **Performance**: Lightweight, fast-loading components
6. **Trust**: Professional, healthcare-appropriate design language

### User Roles & Design

- **Admin**: Full dashboard with data-dense tables and comprehensive controls
- **Staff**: Focused interfaces for patient management and predictions
- **Patient**: Simple, clear displays of personal health data

---

## Color System

### Primary Palette

Based on Bootstrap 5 with healthcare-appropriate customizations:

```css
/* Primary Colors */
--bs-primary: #0d6efd;      /* Main brand color - links, primary actions */
--bs-secondary: #6c757d;    /* Secondary text and borders */
--bs-success: #198754;      /* Success states, "Normal" diagnosis */
--bs-danger: #dc3545;       /* Errors, "COVID" diagnosis */
--bs-warning: #ffc107;      /* Warnings, "Viral Pneumonia" */
--bs-info: #0dcaf0;         /* Info messages, "Lung Opacity" */
--bs-light: #f8f9fa;        /* Light backgrounds */
--bs-dark: #212529;         /* Dark text, headers */
```

### Semantic Colors

| Use Case | Color | Variable | Example |
|----------|-------|----------|---------|
| Positive diagnosis (Normal) | Green | `--bs-success` | "No COVID detected" |
| COVID diagnosis | Red | `--bs-danger` | "COVID-19 Positive" |
| Viral Pneumonia | Yellow | `--bs-warning` | "Viral Pneumonia detected" |
| Lung Opacity | Blue | `--bs-info` | "Lung opacity detected" |
| Pending/Processing | Gray | `--bs-secondary` | "Processing..." |
| Confirmed/Complete | Green | `--bs-success` | "Completed" |
| Cancelled | Gray | `--bs-secondary` | "Cancelled" |

### Text Colors

```css
.text-primary    /* Links, primary text */
.text-secondary  /* Muted text, labels */
.text-success    /* Success messages */
.text-danger     /* Error messages */
.text-warning    /* Warning messages */
.text-info       /* Info messages */
.text-muted      /* Disabled or less important text */
.text-dark       /* Main body text */
```

### Background Colors

```css
.bg-primary      /* Primary background */
.bg-light        /* Page backgrounds */
.bg-white        /* Card backgrounds */
.bg-success      /* Success alerts */
.bg-danger       /* Error alerts */
.bg-warning      /* Warning alerts */
.bg-info         /* Info alerts */
```

---

## Typography

### Font Stack

```css
font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue",
             "Noto Sans", "Liberation Sans", Arial, sans-serif;
```

Uses system fonts for optimal performance and native look.

### Type Scale

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| `<h1>` | 2.5rem (40px) | 500 | 1.2 | Page titles |
| `<h2>` | 2rem (32px) | 500 | 1.2 | Section headers |
| `<h3>` | 1.75rem (28px) | 500 | 1.2 | Subsection headers |
| `<h4>` | 1.5rem (24px) | 500 | 1.2 | Card titles |
| `<h5>` | 1.25rem (20px) | 500 | 1.2 | Minor headings |
| `<h6>` | 1rem (16px) | 500 | 1.2 | Small headings |
| Body | 1rem (16px) | 400 | 1.5 | Regular text |
| Small | 0.875rem (14px) | 400 | 1.5 | Secondary text |

### Typography Classes

```css
.display-1 to .display-6  /* Large display text */
.fs-1 to .fs-6            /* Font size utilities */
.fw-light                 /* Light weight (300) */
.fw-normal                /* Normal weight (400) */
.fw-bold                  /* Bold weight (700) */
.fst-italic               /* Italic style */
.text-uppercase           /* UPPERCASE */
.text-lowercase           /* lowercase */
.text-capitalize          /* Capitalize Each Word */
```

### Usage Guidelines

- **Headers**: Use semantic heading tags (`<h1>` - `<h6>`) for proper document structure
- **Body text**: 1rem (16px) for optimal readability
- **Small text**: Use `.small` or `.text-muted` for secondary information
- **Emphasis**: Use `<strong>` for important text, `<em>` for emphasis
- **Line length**: Max 80 characters per line for readability

---

## Spacing & Layout

### Spacing Scale

Based on Bootstrap's spacing utilities (multiples of 0.25rem = 4px):

| Class | Size | Pixels | Usage |
|-------|------|--------|-------|
| `.p-0`, `.m-0` | 0 | 0px | Remove spacing |
| `.p-1`, `.m-1` | 0.25rem | 4px | Minimal spacing |
| `.p-2`, `.m-2` | 0.5rem | 8px | Tight spacing |
| `.p-3`, `.m-3` | 1rem | 16px | **Default spacing** |
| `.p-4`, `.m-4` | 1.5rem | 24px | Comfortable spacing |
| `.p-5`, `.m-5` | 3rem | 48px | Section spacing |

### Container Widths

```css
.container         /* Max width: 1140px (responsive) */
.container-fluid   /* Full width */
.container-sm      /* Max width: 540px */
.container-md      /* Max width: 720px */
.container-lg      /* Max width: 960px */
.container-xl      /* Max width: 1140px */
.container-xxl     /* Max width: 1320px */
```

### Grid System

12-column grid with responsive breakpoints:

```html
<div class="row">
    <div class="col-md-6">Half width on medium+ screens</div>
    <div class="col-md-6">Half width on medium+ screens</div>
</div>
```

**Breakpoints:**
- `xs`: < 576px (phones)
- `sm`: ≥ 576px (phones landscape)
- `md`: ≥ 768px (tablets)
- `lg`: ≥ 992px (desktops)
- `xl`: ≥ 1200px (large desktops)
- `xxl`: ≥ 1400px (extra large)

### Layout Patterns

**Dashboard Layout:**
```html
<div class="container-fluid">
    <div class="row">
        <!-- Sidebar (optional) -->
        <aside class="col-lg-3 col-md-4">...</aside>

        <!-- Main content -->
        <main class="col-lg-9 col-md-8">...</main>
    </div>
</div>
```

**Card Grid:**
```html
<div class="row g-4">  <!-- g-4 = gap of 1.5rem -->
    <div class="col-lg-4 col-md-6">
        <div class="card">...</div>
    </div>
    <!-- Repeat -->
</div>
```

---

## Components

### Cards

Standard container for content grouping:

```html
<div class="card">
    <div class="card-header">
        <h5 class="card-title mb-0">Title</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Content goes here</p>
    </div>
    <div class="card-footer text-muted">
        Footer text
    </div>
</div>
```

**Card Variations:**
- `.card-body` padding: 1.25rem (20px)
- `.card-header` background: Light gray
- Use `.card-img-top` for images
- Use `.card.shadow-sm` for subtle elevation

### Badges

Status indicators:

```html
<!-- Diagnosis badges -->
<span class="badge bg-success">Normal</span>
<span class="badge bg-danger">COVID-19</span>
<span class="badge bg-warning text-dark">Viral Pneumonia</span>
<span class="badge bg-info text-dark">Lung Opacity</span>

<!-- Status badges -->
<span class="badge bg-primary">Scheduled</span>
<span class="badge bg-secondary">Pending</span>
```

**Using template tags:**
```django
{% load common_tags %}
{% status_badge prediction.diagnosis %}
{% confidence_badge prediction.confidence %}
```

### Alerts

User notifications:

```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
    <strong>Success!</strong> Your changes have been saved.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

**Alert Types:**
- `.alert-primary` - General info
- `.alert-success` - Success messages
- `.alert-danger` - Errors
- `.alert-warning` - Warnings
- `.alert-info` - Informational

### Buttons

Primary actions:

```html
<!-- Primary action -->
<button class="btn btn-primary">Save</button>

<!-- Secondary action -->
<button class="btn btn-outline-secondary">Cancel</button>

<!-- Danger action -->
<button class="btn btn-danger">Delete</button>

<!-- Sizes -->
<button class="btn btn-lg">Large</button>
<button class="btn btn-sm">Small</button>
```

**Button Guidelines:**
- Use `.btn-primary` for primary actions (one per screen)
- Use `.btn-outline-*` for secondary actions
- Use `.btn-danger` for destructive actions (with confirmation)
- Use `.btn-link` for tertiary actions
- Always include descriptive text (no icon-only buttons)

### Tables

Data display:

```html
<table class="table table-striped table-hover">
    <thead>
        <tr>
            <th>Patient Name</th>
            <th>Diagnosis</th>
            <th>Confidence</th>
            <th>Date</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John Doe</td>
            <td><span class="badge bg-success">Normal</span></td>
            <td>95.2%</td>
            <td>2024-11-22</td>
            <td><a href="#" class="btn btn-sm btn-primary">View</a></td>
        </tr>
    </tbody>
</table>
```

**Table Modifiers:**
- `.table-striped` - Zebra striping
- `.table-hover` - Hover effect
- `.table-bordered` - Borders
- `.table-sm` - Compact padding
- `.table-responsive` - Horizontal scroll on small screens

### Modals

Dialog boxes:

```html
<div class="modal fade" id="confirmModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirm Action</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Are you sure you want to proceed?</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary">Confirm</button>
            </div>
        </div>
    </div>
</div>
```

### Pagination

```django
{% load common_tags %}
{% render_pagination page_obj %}
```

---

## Forms

### Form Layout

```html
<form class="needs-validation" novalidate>
    <div class="mb-3">
        <label for="firstName" class="form-label">First Name</label>
        <input type="text" class="form-control" id="firstName" required>
        <div class="invalid-feedback">Please provide a first name.</div>
    </div>

    <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" class="form-control" id="email" required>
        <div class="invalid-feedback">Please provide a valid email.</div>
    </div>

    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Form Controls

Using common widgets:

```python
from common.widgets import (
    BootstrapTextInput,
    BootstrapEmailInput,
    BootstrapSelect,
    BootstrapDateInput,
    BootstrapTextarea,
)

class MyForm(forms.ModelForm):
    class Meta:
        widgets = {
            'name': BootstrapTextInput(attrs={'placeholder': 'Full name'}),
            'email': BootstrapEmailInput(),
            'status': BootstrapSelect(choices=STATUS_CHOICES),
            'date': BootstrapDateInput(),
            'notes': BootstrapTextarea(attrs={'rows': 5}),
        }
```

### Validation States

```html
<!-- Valid -->
<input type="text" class="form-control is-valid">
<div class="valid-feedback">Looks good!</div>

<!-- Invalid -->
<input type="text" class="form-control is-invalid">
<div class="invalid-feedback">Please provide a valid value.</div>
```

---

## Icons

### Bootstrap Icons

Using Bootstrap Icons CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
```

### Common Icons

| Icon | Class | Usage |
|------|-------|-------|
| ✓ | `.bi-check-circle` | Success, Normal diagnosis |
| ✗ | `.bi-x-circle` | Error, Failed |
| 🦠 | `.bi-virus` | COVID diagnosis |
| 🫁 | `.bi-lungs` | Lung-related |
| 📅 | `.bi-calendar` | Dates, appointments |
| 👤 | `.bi-person` | User, patient |
| 📊 | `.bi-graph-up` | Statistics, analytics |
| ⚙️ | `.bi-gear` | Settings |
| 🏠 | `.bi-house` | Home, dashboard |

### Usage

```html
<i class="bi bi-check-circle text-success"></i>
<i class="bi bi-virus text-danger fs-4"></i>

<!-- With template tags -->
{% load common_tags %}
{% icon 'check-circle' 'fs-4' 'text-success' %}
```

---

## Responsive Design

### Mobile-First Approach

Always design for mobile first, then enhance for larger screens:

```html
<!-- Stack on mobile, side-by-side on tablets+ -->
<div class="row">
    <div class="col-md-6">Content 1</div>
    <div class="col-md-6">Content 2</div>
</div>
```

### Responsive Utilities

```css
.d-none .d-md-block    /* Hidden on mobile, visible on tablets+ */
.d-block .d-md-none    /* Visible on mobile, hidden on tablets+ */
```

### Breakpoint Guidelines

- **Mobile (< 768px)**: Single column, stacked layout, touch-friendly targets
- **Tablet (768px - 991px)**: 2-column layout where appropriate
- **Desktop (≥ 992px)**: Full multi-column layouts, data tables

---

## Accessibility

### WCAG 2.1 AA Compliance

1. **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
2. **Keyboard Navigation**: All interactive elements accessible via keyboard
3. **Screen Readers**: Proper ARIA labels and semantic HTML
4. **Focus Indicators**: Visible focus states on all interactive elements

### Best Practices

```html
<!-- Semantic HTML -->
<nav aria-label="Main navigation">...</nav>
<main>...</main>
<aside aria-label="Sidebar">...</aside>

<!-- ARIA labels -->
<button aria-label="Close dialog">×</button>
<img src="xray.jpg" alt="Chest X-ray showing normal lungs">

<!-- Form labels -->
<label for="email">Email Address</label>
<input type="email" id="email" name="email">

<!-- Skip link -->
<a href="#main-content" class="visually-hidden-focusable">Skip to main content</a>
```

---

## Usage Examples

### Dashboard Card

```html
<div class="card shadow-sm">
    <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">
            <i class="bi bi-graph-up me-2"></i>Recent Predictions
        </h5>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <!-- Table content -->
            </table>
        </div>
    </div>
    <div class="card-footer">
        <a href="{% url 'predictions:list' %}" class="btn btn-sm btn-primary">
            View All Predictions
        </a>
    </div>
</div>
```

### Prediction Result Card

```django
{% load common_tags %}

<div class="card">
    <div class="card-body">
        <h5 class="card-title">Prediction Result</h5>
        <div class="row">
            <div class="col-md-6">
                <img src="{{ prediction.xray.original_image.url }}" class="img-fluid rounded" alt="X-ray">
            </div>
            <div class="col-md-6">
                <dl>
                    <dt>Diagnosis</dt>
                    <dd>{% diagnosis_badge prediction.diagnosis %}</dd>

                    <dt>Confidence</dt>
                    <dd>{% confidence_badge prediction.confidence %}</dd>

                    <dt>Date</dt>
                    <dd>{{ prediction.created_at|format_datetime }}</dd>

                    <dt>Status</dt>
                    <dd>{% status_badge prediction.status %}</dd>
                </dl>
            </div>
        </div>
    </div>
</div>
```

---

## Summary

This design system ensures:

✅ **Consistency** - All modules look and feel the same
✅ **Accessibility** - WCAG 2.1 AA compliant
✅ **Responsiveness** - Works on all devices
✅ **Maintainability** - Centralized components and utilities
✅ **Performance** - Lightweight, optimized code
✅ **Professionalism** - Healthcare-appropriate design

**For implementation details, see:**
- `common/widgets.py` - Form widgets
- `common/templatetags/common_tags.py` - Template tags
- `templates/components/` - Reusable components
- Bootstrap 5 Documentation - https://getbootstrap.com/docs/5.3/

---

**Version History:**
- 1.0.0 (2025-11-22): Initial design system documentation

