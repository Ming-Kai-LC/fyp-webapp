---
name: UI Design System
description: Enforces consistent, mobile-first UI/UX design system using Bootstrap 5. Auto-applies design patterns, responsive layouts, color schemes, and component styles for all templates and interfaces.
---

# UI Design System

**Version:** 2.0.0 (Merged from ui-ux-consistency + mobile-responsive)
**Last Updated:** 2025-11-23
**Status:** ⭐ MANDATORY - All UI must follow this design system
**Auto-apply:** YES - When creating/modifying templates, forms, dashboards, navigation

---

## Purpose

This skill ensures consistent visual design AND mobile-first responsive behavior across all user interfaces in the COVID-19 Detection webapp.

**Covers:**
- Design system (colors, typography, spacing, components)
- Mobile-first responsive design
- Bootstrap 5 patterns and utilities
- Accessibility standards (WCAG 2.1 AA)

**Result:** 100% consistent UI, fully responsive on all devices

---

## When This Skill Auto-Triggers

**ALWAYS apply when:**
- Creating new templates or pages
- Modifying existing UI components
- Adding forms, tables, or dashboards
- Creating navigation or card layouts
- Building any user-facing interface
- Refactoring template code

---

## Core Principles

1. **Mobile-First Approach** - Design for mobile (375px), then scale up
2. **Consistent Design Language** - Use design system tokens (colors, typography, spacing)
3. **Bootstrap 5 Grid System** - Responsive grid with breakpoints
4. **Touch-Friendly UI** - Minimum 44x44px touch targets
5. **Accessibility First** - WCAG 2.1 AA compliance
6. **Component Reusability** - Use foundation components from `templates/components/`

---

## Design System Tokens

### Color Palette (Bootstrap 5 Extended)

**Primary Colors:**
```css
Primary:   #0d6efd  /* Blue - main actions, links */
Secondary: #6c757d  /* Gray - secondary actions */
Success:   #198754  /* Green - COVID negative, success states */
Danger:    #dc3545  /* Red - COVID positive, errors */
Warning:   #ffc107  /* Yellow - pending validation, warnings */
Info:      #0dcaf0  /* Cyan - informational messages */
Light:     #f8f9fa  /* Light backgrounds, cards */
Dark:      #212529  /* Text, dark mode backgrounds */
```

**Usage:**
- COVID positive → `bg-danger`, `text-danger`, `badge bg-danger`
- COVID negative / Normal → `bg-success`, `text-success`
- Pending validation → `bg-warning text-dark`
- Informational → `bg-info`, `text-info`

---

### Typography Scale

**Font Family:**
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
             "Helvetica Neue", Arial, sans-serif;
```

**Font Sizes (Bootstrap 5):**
- `display-1` to `display-6` - Hero sections, large headings
- `h1` to `h6` (or classes) - Section headings
- `fs-1` to `fs-6` - Responsive font sizes
- `lead` - Introductory text, emphasis
- `small` or `text-muted` - Secondary information
- **Default body:** 16px (1rem) - never smaller for readability

**Responsive Typography:**
```html
<!-- Scales automatically on different screens -->
<h1 class="display-4">COVID-19 Detection</h1>
<p class="lead">AI-powered chest X-ray analysis</p>
<p class="fs-5">Regular paragraph text</p>
<small class="text-muted">Last updated: 2 hours ago</small>
```

---

### Spacing System

**Bootstrap Spacing Scale (0-5):**
- **0**: 0
- **1**: 0.25rem (4px)
- **2**: 0.5rem (8px)
- **3**: 1rem (16px)
- **4**: 1.5rem (24px)
- **5**: 3rem (48px)

**Responsive Spacing:**
```html
<!-- Different spacing on different screens -->
<div class="mt-3 mt-md-5">  <!-- 1rem on mobile, 3rem on desktop -->
<div class="p-2 p-lg-4">    <!-- 0.5rem padding mobile, 1.5rem desktop -->
<div class="mb-4">          <!-- Consistent 1.5rem bottom margin -->
```

**Common Patterns:**
- Cards: `mb-3` or `mb-4` spacing between
- Sections: `my-4` or `my-5` vertical spacing
- Form fields: `mb-3` between fields
- Buttons: `ms-2` for inline spacing

---

## Responsive Breakpoints

### Bootstrap 5 Breakpoints

| Name | Min Width | Max Width | Device |
|------|-----------|-----------|--------|
| xs | <576px | - | Mobile (default) |
| sm | ≥576px | <768px | Large phones |
| md | ≥768px | <992px | Tablets |
| lg | ≥992px | <1200px | Desktops |
| xl | ≥1200px | <1400px | Large desktops |
| xxl | ≥1400px | - | Extra large screens |

### Required Meta Tag

**MUST be in every template:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Mobile-First Grid Pattern

**Always start with mobile (col-12), then add larger breakpoints:**
```html
<div class="row g-4">
    <!-- 1 column mobile, 2 on tablet, 3 on desktop, 4 on large -->
    <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <div class="card">...</div>
    </div>
</div>
```

**Common Grid Patterns:**
- **Full width mobile, 2 cols desktop:** `col-12 col-md-6`
- **Full width mobile, 3 cols desktop:** `col-12 col-md-4`
- **2 cols mobile, 4 cols desktop:** `col-6 col-lg-3`
- **Sidebar layout:** `col-12 col-lg-8` + `col-12 col-lg-4`

---

## Component Patterns

### 1. Cards (Consistent Structure)

**Standard Card:**
```html
<div class="card shadow-sm">
    <div class="card-header bg-primary text-white">
        <h5 class="mb-0">
            <i class="bi bi-icon"></i> Title
        </h5>
    </div>
    <div class="card-body">
        <p>Card content here</p>
    </div>
    <div class="card-footer text-muted">
        Optional footer
    </div>
</div>
```

**Responsive Card Grid:**
```html
<div class="container">
    <div class="row g-4">
        <div class="col-12 col-sm-6 col-md-4">
            <div class="card h-100">  <!-- h-100 for equal height -->
                <img src="..." class="card-img-top img-fluid" alt="...">
                <div class="card-body">
                    <h5 class="card-title">Title</h5>
                    <p class="card-text">Description</p>
                    <a href="#" class="btn btn-primary w-100">Action</a>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

### 2. Buttons (Consistent Sizing & Icons)

**Button Sizes:**
```html
<!-- Default -->
<button class="btn btn-primary">
    <i class="bi bi-check-circle"></i> Submit
</button>

<!-- Large (recommended for mobile primary actions) -->
<button class="btn btn-primary btn-lg">
    <i class="bi bi-check-circle"></i> Submit
</button>

<!-- Small (for inline actions) -->
<button class="btn btn-sm btn-outline-primary">
    <i class="bi bi-eye"></i> View
</button>
```

**Button Variants:**
```html
<!-- Primary action -->
<button class="btn btn-primary">Primary Action</button>

<!-- Secondary action -->
<button class="btn btn-outline-primary">Secondary Action</button>

<!-- Destructive action -->
<button class="btn btn-danger">
    <i class="bi bi-trash"></i> Delete
</button>

<!-- Full width on mobile -->
<button class="btn btn-primary w-100 w-md-auto">
    Responsive Button
</button>
```

**Touch-Friendly:** Minimum 44x44px target area (use `btn-lg` on mobile)

---

### 3. Forms (Mobile-First Layout)

**Responsive Form Pattern:**
```html
<form method="post">
    {% csrf_token %}

    <!-- Full width on mobile, multi-column on desktop -->
    <div class="row g-3">
        <div class="col-12 col-md-6">
            <label for="firstName" class="form-label">First Name</label>
            <input type="text" class="form-control" id="firstName" required>
        </div>

        <div class="col-12 col-md-6">
            <label for="lastName" class="form-label">Last Name</label>
            <input type="text" class="form-control" id="lastName" required>
        </div>

        <div class="col-12">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" required>
            <div class="form-text">We'll never share your email</div>
        </div>

        <div class="col-12">
            <button type="submit" class="btn btn-primary w-100 w-md-auto">
                <i class="bi bi-save"></i> Save
            </button>
        </div>
    </div>
</form>
```

**Form Best Practices:**
- Labels ALWAYS above inputs (mobile-friendly)
- Full-width inputs on mobile: `w-100`
- Proper spacing: `mb-3` between fields or use `row g-3`
- Submit button full-width on mobile, auto-width on desktop

---

### 4. Tables (Responsive Wrapper)

**ALWAYS wrap tables for horizontal scroll on mobile:**
```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Patient</th>
                <th>Diagnosis</th>
                <th>Date</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>John Doe</td>
                <td><span class="badge bg-success">Normal</span></td>
                <td>2025-11-23</td>
                <td>
                    <a href="#" class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-eye"></i> View
                    </a>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

**Table Variants:**
- `table-hover` - Hover effect on rows
- `table-striped` - Zebra striping
- `table-bordered` - Borders around cells
- `table-sm` - Compact table (smaller padding)

---

### 5. Badges (Status Indicators)

**Diagnosis Badges:**
```html
<!-- COVID Positive -->
<span class="badge bg-danger">
    <i class="bi bi-shield-exclamation"></i> COVID
</span>

<!-- Normal -->
<span class="badge bg-success">
    <i class="bi bi-check-circle"></i> Normal
</span>

<!-- Pending Validation -->
<span class="badge bg-warning text-dark">
    <i class="bi bi-hourglass"></i> Pending
</span>

<!-- Validated -->
<span class="badge bg-success">
    <i class="bi bi-check-circle-fill"></i> Validated
</span>
```

**Badge Sizes:**
```html
<span class="badge bg-primary fs-6">Large badge</span>
<span class="badge bg-primary">Default badge</span>
<span class="badge bg-primary small">Small badge</span>
```

---

### 6. Alerts (User Feedback)

**Alert Pattern:**
```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
    <i class="bi bi-check-circle-fill"></i>
    <strong>Success!</strong> Your X-ray has been uploaded successfully.
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>

<div class="alert alert-danger" role="alert">
    <i class="bi bi-exclamation-triangle-fill"></i>
    <strong>Error!</strong> Upload failed. Please try again.
</div>

<div class="alert alert-warning" role="alert">
    <i class="bi bi-exclamation-circle-fill"></i>
    <strong>Warning!</strong> This prediction requires validation.
</div>

<div class="alert alert-info" role="alert">
    <i class="bi bi-info-circle-fill"></i>
    <strong>Info:</strong> Processing may take up to 30 seconds.
</div>
```

---

### 7. Navigation (Responsive)

**Navbar Pattern:**
```html
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
        <a class="navbar-brand" href="{% url 'home' %}">
            <i class="bi bi-hospital"></i> COVID-19 Detection
        </a>

        <!-- Hamburger menu for mobile -->
        <button class="navbar-toggler" type="button"
                data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>

        <!-- Collapsible menu -->
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'dashboard' %}">
                        <i class="bi bi-speedometer2"></i> Dashboard
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'upload' %}">
                        <i class="bi bi-cloud-upload"></i> Upload
                    </a>
                </li>
            </ul>
        </div>
    </div>
</nav>
```

**Key Points:**
- `navbar-expand-lg` - Collapses on screens <992px
- Hamburger menu automatically appears on mobile
- `ms-auto` - Aligns menu items to the right

---

### 8. Images (Responsive)

**ALWAYS use `img-fluid` for responsive images:**
```html
<!-- Responsive image (scales with container) -->
<img src="xray.jpg" class="img-fluid" alt="Chest X-ray">

<!-- Responsive with rounded corners -->
<img src="profile.jpg" class="img-fluid rounded" alt="Profile">

<!-- Responsive circle (for avatars) -->
<img src="avatar.jpg" class="img-fluid rounded-circle" alt="User">

<!-- Responsive thumbnail -->
<img src="thumbnail.jpg" class="img-thumbnail" alt="Thumbnail">
```

**Image in Card:**
```html
<div class="card">
    <img src="..." class="card-img-top img-fluid" alt="...">
    <div class="card-body">...</div>
</div>
```

---

## Icon System (Bootstrap Icons)

### Consistent Icon Mapping

**Feature Icons:**
- Upload: `bi-cloud-upload`
- View/Results: `bi-eye`
- Edit: `bi-pencil`
- Delete: `bi-trash`
- Save: `bi-save`, `bi-check-circle`
- Cancel: `bi-x-circle`
- Back: `bi-arrow-left`

**User Roles:**
- Admin: `bi-gear`, `bi-shield-lock`
- Doctor/Staff: `bi-hospital`, `bi-person-badge`
- Patient: `bi-person`, `bi-person-circle`

**Diagnosis:**
- COVID Positive: `bi-shield-exclamation`, `bi-virus`
- Normal: `bi-check-circle`, `bi-shield-check`
- Pending: `bi-hourglass`, `bi-clock`
- Validated: `bi-check-circle-fill`

**Dashboard:**
- Dashboard: `bi-speedometer2`
- Statistics: `bi-bar-chart`, `bi-graph-up`
- Reports: `bi-file-earmark-text`
- X-Ray: `bi-image`, `bi-file-medical`

**Actions:**
- Download: `bi-download`
- Print: `bi-printer`
- Share: `bi-share`
- Filter: `bi-funnel`
- Search: `bi-search`

---

## Responsive Utilities

### Display Utilities

**Show/Hide on Different Screens:**
```html
<!-- Hidden on mobile, visible on desktop -->
<div class="d-none d-md-block">Desktop content</div>

<!-- Visible on mobile, hidden on desktop -->
<div class="d-block d-md-none">Mobile content</div>

<!-- Different layouts for different screens -->
<div class="d-flex flex-column flex-md-row">
    <!-- Stacks vertically on mobile, horizontal on desktop -->
</div>
```

### Text Alignment

```html
<!-- Center on mobile, left on desktop -->
<p class="text-center text-md-start">Responsive text</p>

<!-- Right align on large screens -->
<p class="text-end text-lg-start">Right on mobile, left on desktop</p>
```

### Margin & Padding

```html
<!-- Responsive spacing -->
<div class="mt-3 mt-md-5">  <!-- 1rem on mobile, 3rem on desktop -->
<div class="p-2 p-lg-4">    <!-- Small padding mobile, larger desktop -->
```

---

## Accessibility (WCAG 2.1 AA)

### Color Contrast

**Minimum ratios:**
- Normal text (18px): 4.5:1
- Large text (24px): 3:1
- UI components: 3:1

**Bootstrap defaults meet WCAG AA** - don't override without checking contrast

### Semantic HTML

```html
<!-- ✅ GOOD: Semantic -->
<nav>...</nav>
<main>...</main>
<article>...</article>
<aside>...</aside>

<!-- ❌ BAD: Non-semantic -->
<div class="nav">...</div>
<div class="main">...</div>
```

### ARIA Labels

```html
<!-- Form labels -->
<label for="email">Email</label>
<input id="email" type="email" required>

<!-- Icon-only buttons need aria-label -->
<button class="btn btn-primary" aria-label="Delete">
    <i class="bi bi-trash"></i>
</button>

<!-- Screen reader text -->
<span class="visually-hidden">Loading...</span>
```

### Keyboard Navigation

- All interactive elements must be keyboard accessible
- Logical tab order (use `tabindex` sparingly)
- Focus states visible (don't remove `:focus` outlines)

---

## Testing Checklist

**Before completing any UI task, verify:**

### Mobile Testing (375px - iPhone SE)
- ✅ Navigation collapses to hamburger menu
- ✅ Forms are usable (labels above inputs)
- ✅ Buttons are large enough (44x44px minimum)
- ✅ Text is readable (minimum 16px)
- ✅ No horizontal scrolling
- ✅ Cards stack vertically
- ✅ Images scale properly

### Tablet Testing (768px - iPad)
- ✅ Grid transitions work (2-column layouts)
- ✅ Navigation expands if using `navbar-expand-md`
- ✅ Proper spacing adjustments
- ✅ Forms use available space

### Desktop Testing (1920px)
- ✅ Maximum width containers work
- ✅ Multi-column layouts display correctly
- ✅ Navigation fully expanded
- ✅ No wasted whitespace

### Cross-Browser
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (especially important for iOS)

### Accessibility
- ✅ Keyboard navigation works
- ✅ Screen reader compatible
- ✅ Color contrast meets WCAG AA
- ✅ Focus indicators visible

---

## Common Issues to Avoid

### ❌ DON'T DO THIS:

**1. Fixed Widths**
```html
<!-- ❌ WRONG -->
<div style="width: 800px;">...</div>
```
**✅ DO THIS:** Use responsive classes
```html
<div class="w-100 w-lg-75">...</div>
```

**2. Tiny Touch Targets**
```html
<!-- ❌ WRONG -->
<button class="btn btn-sm">Delete</button>  <!-- Too small for mobile -->
```
**✅ DO THIS:** Use larger buttons on mobile
```html
<button class="btn btn-danger">
    <i class="bi bi-trash"></i> Delete
</button>
```

**3. Horizontal Scrolling**
```html
<!-- ❌ WRONG -->
<table>...</table>  <!-- Overflows on mobile -->
```
**✅ DO THIS:** Wrap in responsive container
```html
<div class="table-responsive">
    <table>...</table>
</div>
```

**4. Unreadable Text**
```html
<!-- ❌ WRONG -->
<p style="font-size: 12px;">...</p>  <!-- Too small -->
```
**✅ DO THIS:** Use minimum 16px
```html
<p>...</p>  <!-- Bootstrap default 16px -->
```

**5. Missing Viewport Meta**
```html
<!-- ❌ WRONG -->
<head>
    <title>Page</title>
</head>
```
**✅ DO THIS:** Include viewport meta
```html
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page</title>
</head>
```

**6. Non-Responsive Images**
```html
<!-- ❌ WRONG -->
<img src="photo.jpg" width="800">
```
**✅ DO THIS:** Use img-fluid
```html
<img src="photo.jpg" class="img-fluid" alt="Description">
```

**7. Hardcoded Colors**
```html
<!-- ❌ WRONG -->
<div style="background-color: #ff0000;">...</div>
```
**✅ DO THIS:** Use Bootstrap classes
```html
<div class="bg-danger text-white">...</div>
```

---

## Integration with Foundation Components

This skill works seamlessly with **foundation-components**:
- Use `BootstrapTextInput`, `BootstrapSelect`, etc. (automatically styled)
- Use `{% include 'components/card.html' %}` (already responsive)
- Use `{% include 'components/alert.html' %}` (already accessible)
- Use `{% status_badge %}` template tag (correct color mapping)

**Design system + Foundation components = Perfect consistency**

---

## Healthcare UI Patterns

Healthcare applications require specialized UI components that handle sensitive medical data with appropriate visual hierarchy, clarity, and patient privacy considerations.

---

### 10.1 Patient Data Cards with PHI Protection

**Patient Information Card:**

```html
<div class="card shadow-sm border-primary mb-4">
    <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
            <i class="bi bi-person-circle"></i> Patient Information
        </h5>
        <span class="badge bg-light text-primary">
            <i class="bi bi-shield-lock"></i> PHI Protected
        </span>
    </div>
    <div class="card-body">
        <div class="row g-3">
            <div class="col-12 col-md-6">
                <div class="d-flex align-items-start mb-2">
                    <i class="bi bi-person text-primary me-2 fs-5"></i>
                    <div>
                        <small class="text-muted d-block">Full Name</small>
                        <strong>{{ patient.full_name }}</strong>
                    </div>
                </div>
            </div>

            <div class="col-12 col-md-6">
                <div class="d-flex align-items-start mb-2">
                    <i class="bi bi-calendar text-primary me-2 fs-5"></i>
                    <div>
                        <small class="text-muted d-block">Date of Birth</small>
                        <strong>{{ patient.dob|date:"d M Y" }}</strong>
                        <span class="text-muted small">(Age: {{ patient.age }})</span>
                    </div>
                </div>
            </div>

            <div class="col-12 col-md-6">
                <div class="d-flex align-items-start mb-2">
                    <i class="bi bi-telephone text-primary me-2 fs-5"></i>
                    <div>
                        <small class="text-muted d-block">Contact</small>
                        <strong>{{ patient.phone }}</strong>
                    </div>
                </div>
            </div>

            <div class="col-12 col-md-6">
                <div class="d-flex align-items-start mb-2">
                    <i class="bi bi-gender-ambiguous text-primary me-2 fs-5"></i>
                    <div>
                        <small class="text-muted d-block">Gender</small>
                        <strong>{{ patient.get_gender_display }}</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Key Features:**
- PHI badge to remind staff this is protected data
- Icon-labeled fields for visual scanning
- Responsive grid (1 column mobile, 2 columns tablet+)
- Clear visual hierarchy with small labels + bold values

---

### 10.2 Diagnosis Display with Severity Indicators

**COVID-19 Diagnosis Card:**

```html
<div class="card shadow-sm mb-4 {{ diagnosis.result == 'positive' ? 'border-danger' : 'border-success' }}">
    <div class="card-header {{ diagnosis.result == 'positive' ? 'bg-danger' : 'bg-success' }} text-white">
        <h5 class="mb-0">
            <i class="bi bi-file-medical"></i> Diagnosis Result
        </h5>
    </div>
    <div class="card-body">
        <!-- Result Badge -->
        <div class="text-center mb-4">
            {% if diagnosis.result == 'positive' %}
                <div class="display-1 text-danger mb-3">
                    <i class="bi bi-shield-exclamation"></i>
                </div>
                <h2 class="text-danger fw-bold">COVID-19 Detected</h2>
                <p class="text-muted">Confidence: {{ diagnosis.confidence }}%</p>
            {% else %}
                <div class="display-1 text-success mb-3">
                    <i class="bi bi-shield-check"></i>
                </div>
                <h2 class="text-success fw-bold">Normal - No COVID-19 Detected</h2>
                <p class="text-muted">Confidence: {{ diagnosis.confidence }}%</p>
            {% endif %}
        </div>

        <!-- Severity Meter (for positive cases) -->
        {% if diagnosis.result == 'positive' %}
        <div class="mb-4">
            <label class="form-label fw-bold">Severity Assessment</label>
            <div class="progress" style="height: 30px;">
                <div class="progress-bar bg-danger" role="progressbar"
                     style="width: {{ diagnosis.severity_score }}%"
                     aria-valuenow="{{ diagnosis.severity_score }}"
                     aria-valuemin="0" aria-valuemax="100">
                    {{ diagnosis.severity_score }}%
                </div>
            </div>
            <small class="text-muted d-block mt-1">
                {% if diagnosis.severity_score < 30 %}
                    Mild symptoms expected
                {% elif diagnosis.severity_score < 70 %}
                    Moderate symptoms - monitoring recommended
                {% else %}
                    Severe - immediate medical attention required
                {% endif %}
            </small>
        </div>
        {% endif %}

        <!-- Validation Status -->
        <div class="alert {{ diagnosis.validated ? 'alert-info' : 'alert-warning' }} mb-0">
            <i class="bi {{ diagnosis.validated ? 'bi-check-circle-fill' : 'bi-hourglass' }}"></i>
            <strong>Validation Status:</strong>
            {% if diagnosis.validated %}
                Validated by Dr. {{ diagnosis.validated_by.full_name }} on {{ diagnosis.validated_at|date:"d M Y H:i" }}
            {% else %}
                Pending medical validation
            {% endif %}
        </div>
    </div>
</div>
```

**Severity Color Scale:**
- 0-29%: `bg-success` (Mild)
- 30-69%: `bg-warning` (Moderate)
- 70-100%: `bg-danger` (Severe)

---

### 10.3 Medical Forms with Progressive Disclosure

**Multi-Step Medical History Form:**

```html
<div class="card shadow-sm">
    <div class="card-header bg-primary text-white">
        <h5 class="mb-0">
            <i class="bi bi-clipboard-heart"></i> Medical History
        </h5>
    </div>
    <div class="card-body">
        <!-- Progress Indicator -->
        <div class="mb-4">
            <div class="d-flex justify-content-between mb-2">
                <span class="small fw-bold">Step {{ current_step }} of 4</span>
                <span class="small text-muted">{{ progress_percent }}% Complete</span>
            </div>
            <div class="progress" style="height: 8px;">
                <div class="progress-bar bg-primary" role="progressbar"
                     style="width: {{ progress_percent }}%"
                     aria-valuenow="{{ progress_percent }}"
                     aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
        </div>

        <!-- Step 1: Basic Symptoms -->
        <div id="step1" class="form-step {{ current_step != 1 ? 'd-none' : '' }}">
            <h6 class="mb-3 text-primary fw-bold">
                <i class="bi bi-thermometer"></i> Current Symptoms
            </h6>

            <!-- Checkbox Group with Icons -->
            <div class="row g-3">
                <div class="col-12 col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="fever" name="symptoms" value="fever">
                        <label class="form-check-label" for="fever">
                            <i class="bi bi-thermometer-high text-danger"></i> Fever (>38°C)
                        </label>
                    </div>
                </div>

                <div class="col-12 col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="cough" name="symptoms" value="cough">
                        <label class="form-check-label" for="cough">
                            <i class="bi bi-wind text-primary"></i> Persistent Cough
                        </label>
                    </div>
                </div>

                <div class="col-12 col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="breathless" name="symptoms" value="breathless">
                        <label class="form-check-label" for="breathless">
                            <i class="bi bi-lungs text-danger"></i> Difficulty Breathing
                        </label>
                    </div>
                </div>

                <div class="col-12 col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="fatigue" name="symptoms" value="fatigue">
                        <label class="form-check-label" for="fatigue">
                            <i class="bi bi-battery-half text-warning"></i> Fatigue
                        </label>
                    </div>
                </div>
            </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="d-flex justify-content-between mt-4">
            <button type="button" class="btn btn-outline-secondary {{ current_step == 1 ? 'invisible' : '' }}"
                    onclick="previousStep()">
                <i class="bi bi-arrow-left"></i> Previous
            </button>

            <button type="button" class="btn btn-primary {{ current_step == 4 ? 'd-none' : '' }}"
                    onclick="nextStep()">
                Next <i class="bi bi-arrow-right"></i>
            </button>

            <button type="submit" class="btn btn-success {{ current_step != 4 ? 'd-none' : '' }}">
                <i class="bi bi-check-circle"></i> Submit
            </button>
        </div>
    </div>
</div>
```

**Key Features:**
- Progress bar showing completion percentage
- Icon-labeled checkboxes for visual recognition
- Responsive 2-column layout on tablet+
- Clear navigation buttons with contextual visibility

---

### 10.4 Medical Timeline (Treatment History)

**Appointment & Treatment Timeline:**

```html
<div class="card shadow-sm">
    <div class="card-header bg-primary text-white">
        <h5 class="mb-0">
            <i class="bi bi-clock-history"></i> Medical Timeline
        </h5>
    </div>
    <div class="card-body">
        <!-- Timeline Container -->
        <div class="timeline">
            {% for event in medical_events %}
            <div class="timeline-item mb-4">
                <div class="row">
                    <!-- Date Badge (Left Column) -->
                    <div class="col-3 col-md-2 text-end">
                        <span class="badge bg-primary rounded-pill px-3 py-2">
                            {{ event.date|date:"d M" }}<br>
                            <small>{{ event.date|date:"Y" }}</small>
                        </span>
                    </div>

                    <!-- Event Card (Right Column) -->
                    <div class="col-9 col-md-10">
                        <div class="card border-start border-primary border-4">
                            <div class="card-body">
                                <div class="d-flex align-items-start mb-2">
                                    <div class="icon-circle bg-primary bg-opacity-10 text-primary rounded-circle p-2 me-3">
                                        <i class="bi {{ event.icon }} fs-5"></i>
                                    </div>
                                    <div class="flex-grow-1">
                                        <h6 class="mb-1 fw-bold">{{ event.title }}</h6>
                                        <p class="mb-2 text-muted small">
                                            {{ event.description }}
                                        </p>
                                        {% if event.diagnosis %}
                                        <span class="badge {{ event.diagnosis == 'positive' ? 'bg-danger' : 'bg-success' }}">
                                            {{ event.diagnosis|upper }}
                                        </span>
                                        {% endif %}
                                        <small class="text-muted d-block mt-2">
                                            <i class="bi bi-person-badge"></i> {{ event.staff.name }}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>

<style>
.timeline-item:last-child .card {
    border-left-color: #dee2e6 !important;
}

.icon-circle {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
```

**Timeline Icons:**
- X-ray upload: `bi-image`
- Diagnosis: `bi-file-medical`
- Appointment: `bi-calendar-check`
- Prescription: `bi-prescription2`
- Lab test: `bi-clipboard-pulse`

---

### 10.5 X-Ray Image Viewer with Controls

**Interactive X-Ray Display:**

```html
<div class="card shadow-sm">
    <div class="card-header bg-dark text-white">
        <h5 class="mb-0">
            <i class="bi bi-image"></i> Chest X-Ray
        </h5>
    </div>
    <div class="card-body bg-dark p-0">
        <!-- Image Container -->
        <div id="xray-viewer" class="position-relative" style="background: #000;">
            <img id="xray-image"
                 src="{{ xray.image.url }}"
                 class="img-fluid w-100"
                 alt="Chest X-ray"
                 style="cursor: zoom-in;">

            <!-- Zoom Controls Overlay -->
            <div class="position-absolute top-0 end-0 m-3">
                <div class="btn-group-vertical" role="group">
                    <button class="btn btn-light btn-sm" onclick="zoomIn()" aria-label="Zoom In">
                        <i class="bi bi-zoom-in"></i>
                    </button>
                    <button class="btn btn-light btn-sm" onclick="zoomOut()" aria-label="Zoom Out">
                        <i class="bi bi-zoom-out"></i>
                    </button>
                    <button class="btn btn-light btn-sm" onclick="resetZoom()" aria-label="Reset Zoom">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                    <button class="btn btn-light btn-sm" onclick="toggleFullscreen()" aria-label="Fullscreen">
                        <i class="bi bi-fullscreen"></i>
                    </button>
                </div>
            </div>

            <!-- Image Info Overlay -->
            <div class="position-absolute bottom-0 start-0 m-3 text-white">
                <small class="bg-dark bg-opacity-75 px-2 py-1 rounded">
                    <i class="bi bi-calendar"></i> {{ xray.created_at|date:"d M Y H:i" }}
                </small>
            </div>
        </div>
    </div>

    <!-- Metadata Footer -->
    <div class="card-footer bg-light">
        <div class="row g-2 small">
            <div class="col-6 col-md-3">
                <strong>Resolution:</strong> {{ xray.resolution }}
            </div>
            <div class="col-6 col-md-3">
                <strong>File Size:</strong> {{ xray.file_size|filesizeformat }}
            </div>
            <div class="col-6 col-md-3">
                <strong>Format:</strong> {{ xray.format }}
            </div>
            <div class="col-6 col-md-3">
                <strong>Uploaded by:</strong> {{ xray.uploaded_by.name }}
            </div>
        </div>
    </div>
</div>
```

**Key Features:**
- Dark background for medical image viewing
- Floating zoom controls (vertical button group)
- Timestamp and metadata overlays
- Fullscreen capability for detailed analysis
- Responsive image scaling

---

### 10.6 Prescription & Medication Display

**Prescription Card:**

```html
<div class="card shadow-sm border-primary mb-3">
    <div class="card-body">
        <div class="row align-items-center">
            <div class="col-auto">
                <div class="bg-primary bg-opacity-10 text-primary rounded-circle p-3">
                    <i class="bi bi-capsule fs-3"></i>
                </div>
            </div>
            <div class="col">
                <h5 class="mb-1 fw-bold">{{ medication.name }}</h5>
                <p class="mb-1 text-muted small">{{ medication.generic_name }}</p>

                <div class="d-flex flex-wrap gap-2 mt-2">
                    <span class="badge bg-info text-dark">
                        <i class="bi bi-clock"></i> {{ medication.dosage }} - {{ medication.frequency }}
                    </span>
                    <span class="badge bg-warning text-dark">
                        <i class="bi bi-calendar-range"></i> {{ medication.duration }} days
                    </span>
                </div>

                {% if medication.notes %}
                <div class="alert alert-warning alert-sm mt-2 mb-0 py-2">
                    <small><i class="bi bi-exclamation-triangle"></i> {{ medication.notes }}</small>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
```

---

## Advanced Accessibility for Medical Apps

Healthcare applications must meet the highest accessibility standards to serve all users, including those with disabilities who may need urgent medical care.

---

### 11.1 Screen Reader Support for Medical Data

**Proper ARIA Labels for Diagnoses:**

```html
<!-- Diagnosis with screen reader context -->
<div class="card" role="region" aria-labelledby="diagnosis-heading">
    <div class="card-header">
        <h5 id="diagnosis-heading">Diagnosis Result</h5>
    </div>
    <div class="card-body">
        <!-- COVID Positive Result -->
        <div class="alert alert-danger" role="alert" aria-live="polite">
            <span class="visually-hidden">Warning: </span>
            <i class="bi bi-shield-exclamation" aria-hidden="true"></i>
            <strong>COVID-19 Detected</strong>
            <span class="visually-hidden">
                with {{ confidence }}% confidence. Please consult with medical staff immediately.
            </span>
        </div>

        <!-- Confidence Score (Readable by Screen Readers) -->
        <div class="mb-3">
            <label class="form-label">Confidence Level</label>
            <div class="progress" style="height: 30px;"
                 role="progressbar"
                 aria-valuenow="{{ confidence }}"
                 aria-valuemin="0"
                 aria-valuemax="100"
                 aria-label="AI diagnosis confidence level: {{ confidence }} percent">
                <div class="progress-bar bg-danger" style="width: {{ confidence }}%;">
                    {{ confidence }}%
                </div>
            </div>
        </div>
    </div>
</div>
```

**Key Patterns:**
- `role="region"` for major sections
- `aria-labelledby` to connect headings
- `aria-live="polite"` for dynamic diagnosis updates
- `visually-hidden` class for screen reader context
- `aria-hidden="true"` on decorative icons
- Descriptive `aria-label` on progress bars and meters

---

### 11.2 Keyboard Navigation for Medical Workflows

**Full Keyboard Accessibility:**

```html
<div class="patient-actions" role="toolbar" aria-label="Patient actions">
    <!-- Each action is keyboard accessible with Tab, Enter/Space -->
    <button class="btn btn-primary"
            data-action="view-history"
            aria-label="View full medical history for {{ patient.name }}">
        <i class="bi bi-clock-history" aria-hidden="true"></i>
        <span class="d-none d-md-inline">History</span>
    </button>

    <button class="btn btn-success"
            data-action="upload-xray"
            aria-label="Upload new X-ray for {{ patient.name }}">
        <i class="bi bi-cloud-upload" aria-hidden="true"></i>
        <span class="d-none d-md-inline">Upload</span>
    </button>

    <button class="btn btn-info"
            data-action="view-reports"
            aria-label="View all reports for {{ patient.name }}">
        <i class="bi bi-file-earmark-text" aria-hidden="true"></i>
        <span class="d-none d-md-inline">Reports</span>
    </button>
</div>

<script>
// Keyboard shortcut support
document.addEventListener('keydown', function(e) {
    // Alt+H = View History
    if (e.altKey && e.key === 'h') {
        document.querySelector('[data-action="view-history"]').click();
    }
    // Alt+U = Upload X-ray
    if (e.altKey && e.key === 'u') {
        document.querySelector('[data-action="upload-xray"]').click();
    }
    // Alt+R = View Reports
    if (e.altKey && e.key === 'r') {
        document.querySelector('[data-action="view-reports"]').click();
    }
});
</script>
```

**Keyboard Navigation Checklist:**
- ✅ Tab order follows logical flow
- ✅ Focus indicators visible (`outline` not removed)
- ✅ All actions accessible via Enter/Space
- ✅ Keyboard shortcuts for common tasks (Alt+Key)
- ✅ Escape closes modals
- ✅ Arrow keys navigate lists/grids

---

### 11.3 High Contrast Mode for Clinical Environments

**Clinical High Contrast CSS:**

```css
/* High contrast mode for clinical viewing */
@media (prefers-contrast: high) {
    :root {
        --bs-primary: #0000EE;  /* Bright blue */
        --bs-danger: #FF0000;   /* Pure red */
        --bs-success: #008000;  /* Pure green */
        --bs-body-bg: #FFFFFF;
        --bs-body-color: #000000;
    }

    .card {
        border: 2px solid #000000 !important;
    }

    .btn {
        border: 2px solid currentColor !important;
    }

    /* Diagnosis badges in high contrast */
    .badge.bg-danger {
        background-color: #FF0000 !important;
        color: #FFFFFF !important;
        border: 2px solid #000000 !important;
    }

    .badge.bg-success {
        background-color: #008000 !important;
        color: #FFFFFF !important;
        border: 2px solid #000000 !important;
    }
}
```

**Manual High Contrast Toggle:**

```html
<!-- High contrast toggle button -->
<button id="contrast-toggle"
        class="btn btn-outline-secondary"
        onclick="toggleHighContrast()"
        aria-label="Toggle high contrast mode"
        aria-pressed="false">
    <i class="bi bi-brightness-high"></i> High Contrast
</button>

<script>
function toggleHighContrast() {
    document.body.classList.toggle('high-contrast');
    const isActive = document.body.classList.contains('high-contrast');
    document.getElementById('contrast-toggle').setAttribute('aria-pressed', isActive);
    localStorage.setItem('highContrast', isActive);
}

// Restore preference
if (localStorage.getItem('highContrast') === 'true') {
    document.body.classList.add('high-contrast');
}
</script>

<style>
body.high-contrast {
    --bs-primary: #0000EE;
    --bs-danger: #FF0000;
    --bs-success: #008000;
    background: #FFFFFF;
    color: #000000;
}

body.high-contrast .card {
    border: 3px solid #000000 !important;
}
</style>
```

---

### 11.4 Voice Navigation Support

**Voice Command Integration:**

```html
<!-- Voice command status indicator -->
<div id="voice-status" class="position-fixed bottom-0 end-0 m-3" style="z-index: 1050;">
    <button class="btn btn-primary btn-lg rounded-circle shadow"
            onclick="toggleVoiceCommands()"
            aria-label="Toggle voice commands"
            title="Voice Commands (Alt+V)">
        <i class="bi bi-mic" id="mic-icon"></i>
    </button>
</div>

<script>
// Web Speech API for voice commands
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript.toLowerCase();
        handleVoiceCommand(command);
    };
}

function handleVoiceCommand(command) {
    // Medical workflow voice commands
    if (command.includes('show patient list')) {
        window.location.href = '/patients/';
    }
    else if (command.includes('upload x-ray') || command.includes('upload xray')) {
        window.location.href = '/detection/upload/';
    }
    else if (command.includes('view dashboard')) {
        window.location.href = '/dashboard/';
    }
    else if (command.includes('show reports')) {
        window.location.href = '/reporting/';
    }
    // Announce confirmation
    speak(`Navigating to ${command}`);
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utterance);
}
</script>
```

**Supported Voice Commands:**
- "Show patient list"
- "Upload X-ray"
- "View dashboard"
- "Show reports"
- "Read diagnosis" (reads diagnosis aloud)
- "Next patient" / "Previous patient"

---

### 11.5 Emergency Accessibility Features

**Critical Alert Pattern:**

```html
<!-- Emergency notification with maximum accessibility -->
<div class="alert alert-danger alert-dismissible fade show"
     role="alert"
     aria-live="assertive"
     aria-atomic="true">
    <div class="d-flex align-items-center mb-2">
        <i class="bi bi-exclamation-triangle-fill fs-1 me-3" aria-hidden="true"></i>
        <div>
            <h4 class="alert-heading mb-1">Critical: Severe COVID-19 Case Detected</h4>
            <p class="mb-0">
                <span class="visually-hidden">Emergency alert: </span>
                Patient {{ patient.name }} requires immediate medical attention.
                Severity score: {{ severity }}%.
            </p>
        </div>
    </div>

    <!-- Emergency action buttons with clear labels -->
    <div class="mt-3">
        <button class="btn btn-light btn-lg me-2"
                onclick="notifyDoctor()"
                aria-label="Notify on-duty doctor immediately">
            <i class="bi bi-telephone-fill" aria-hidden="true"></i>
            Notify Doctor
        </button>
        <button class="btn btn-outline-light btn-lg"
                onclick="viewDetails()"
                aria-label="View full patient details and diagnosis">
            <i class="bi bi-info-circle" aria-hidden="true"></i>
            View Details
        </button>
    </div>

    <button type="button" class="btn-close btn-close-white"
            data-bs-dismiss="alert"
            aria-label="Dismiss emergency alert"></button>
</div>

<script>
// Auto-announce emergency alerts to screen readers
function announceEmergency(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'alert');
    announcement.setAttribute('aria-live', 'assertive');
    announcement.className = 'visually-hidden';
    announcement.textContent = message;
    document.body.appendChild(announcement);

    // Remove after announcement
    setTimeout(() => announcement.remove(), 3000);
}
</script>
```

**Key Features:**
- `aria-live="assertive"` for immediate screen reader notification
- `aria-atomic="true"` reads entire alert, not just changes
- Large, clear action buttons
- Visual + auditory feedback
- Color + icon + text (triple redundancy for critical info)

---

## Animation & Loading States

Medical applications require clear feedback during long-running operations (ML inference, image processing) and smooth transitions to reduce cognitive load.

---

### 12.1 ML Inference Progress Indicator

**X-Ray Processing Loading State:**

```html
<div id="processing-modal" class="modal fade" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-body text-center p-5">
                <!-- Animated Icon -->
                <div class="mb-4">
                    <i class="bi bi-hourglass-split fs-1 text-primary"
                       style="animation: spin 2s linear infinite;"></i>
                </div>

                <!-- Progress Bar -->
                <h5 class="mb-3">Analyzing X-Ray...</h5>
                <div class="progress mb-3" style="height: 25px;">
                    <div id="progress-bar"
                         class="progress-bar progress-bar-striped progress-bar-animated bg-primary"
                         role="progressbar"
                         style="width: 0%"
                         aria-valuenow="0"
                         aria-valuemin="0"
                         aria-valuemax="100">
                        <span id="progress-text">0%</span>
                    </div>
                </div>

                <!-- Status Messages -->
                <p id="status-message" class="text-muted small">
                    <i class="bi bi-info-circle"></i> Preprocessing image...
                </p>

                <!-- Estimated Time -->
                <small class="text-muted">
                    Estimated time: <span id="eta">30 seconds</span>
                </small>
            </div>
        </div>
    </div>
</div>

<style>
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>

<script>
// Simulate ML inference progress
function processXRay() {
    const modal = new bootstrap.Modal(document.getElementById('processing-modal'));
    modal.show();

    const stages = [
        { percent: 20, message: 'Preprocessing image...', time: 2000 },
        { percent: 40, message: 'Running AI model inference...', time: 15000 },
        { percent: 70, message: 'Analyzing results...', time: 8000 },
        { percent: 90, message: 'Generating report...', time: 3000 },
        { percent: 100, message: 'Complete!', time: 2000 }
    ];

    let currentStage = 0;

    function updateProgress() {
        if (currentStage < stages.length) {
            const stage = stages[currentStage];

            // Update progress bar
            document.getElementById('progress-bar').style.width = stage.percent + '%';
            document.getElementById('progress-bar').setAttribute('aria-valuenow', stage.percent);
            document.getElementById('progress-text').textContent = stage.percent + '%';

            // Update status message
            document.getElementById('status-message').textContent = stage.message;

            // Update ETA
            const remainingTime = stages.slice(currentStage).reduce((sum, s) => sum + s.time, 0);
            document.getElementById('eta').textContent = Math.ceil(remainingTime / 1000) + ' seconds';

            currentStage++;
            setTimeout(updateProgress, stage.time);
        } else {
            // Processing complete - redirect to results
            setTimeout(() => {
                modal.hide();
                window.location.href = '/detection/results/';
            }, 1000);
        }
    }

    updateProgress();
}
</script>
```

---

### 12.2 Multi-Step Form Progress

**Medical Form Progress Tracker:**

```html
<div class="card shadow-sm mb-4">
    <div class="card-body">
        <!-- Step Indicators -->
        <div class="step-progress mb-4">
            <div class="d-flex justify-content-between position-relative">
                <!-- Progress Line -->
                <div class="progress-line" style="position: absolute; top: 20px; left: 0; right: 0; height: 4px; background: #e9ecef; z-index: 0;">
                    <div class="progress-line-fill bg-primary" style="height: 100%; width: {{ (current_step - 1) * 33 }}%; transition: width 0.3s ease;"></div>
                </div>

                <!-- Step 1 -->
                <div class="step-item text-center {{ current_step >= 1 ? 'active' : '' }}" style="z-index: 1;">
                    <div class="step-circle bg-{{ current_step >= 1 ? 'primary' : 'light' }} text-{{ current_step >= 1 ? 'white' : 'muted' }} rounded-circle d-flex align-items-center justify-content-center mx-auto mb-2"
                         style="width: 40px; height: 40px; transition: all 0.3s ease;">
                        {% if current_step > 1 %}
                            <i class="bi bi-check-lg"></i>
                        {% else %}
                            <span>1</span>
                        {% endif %}
                    </div>
                    <small class="fw-bold">Symptoms</small>
                </div>

                <!-- Step 2 -->
                <div class="step-item text-center {{ current_step >= 2 ? 'active' : '' }}" style="z-index: 1;">
                    <div class="step-circle bg-{{ current_step >= 2 ? 'primary' : 'light' }} text-{{ current_step >= 2 ? 'white' : 'muted' }} rounded-circle d-flex align-items-center justify-content-center mx-auto mb-2"
                         style="width: 40px; height: 40px; transition: all 0.3s ease;">
                        {% if current_step > 2 %}
                            <i class="bi bi-check-lg"></i>
                        {% else %}
                            <span>2</span>
                        {% endif %}
                    </div>
                    <small class="fw-bold">Medical History</small>
                </div>

                <!-- Step 3 -->
                <div class="step-item text-center {{ current_step >= 3 ? 'active' : '' }}" style="z-index: 1;">
                    <div class="step-circle bg-{{ current_step >= 3 ? 'primary' : 'light' }} text-{{ current_step >= 3 ? 'white' : 'muted' }} rounded-circle d-flex align-items-center justify-content-center mx-auto mb-2"
                         style="width: 40px; height: 40px; transition: all 0.3s ease;">
                        {% if current_step > 3 %}
                            <i class="bi bi-check-lg"></i>
                        {% else %}
                            <span>3</span>
                        {% endif %}
                    </div>
                    <small class="fw-bold">Contact Info</small>
                </div>

                <!-- Step 4 -->
                <div class="step-item text-center {{ current_step >= 4 ? 'active' : '' }}" style="z-index: 1;">
                    <div class="step-circle bg-{{ current_step >= 4 ? 'primary' : 'light' }} text-{{ current_step >= 4 ? 'white' : 'muted' }} rounded-circle d-flex align-items-center justify-content-center mx-auto mb-2"
                         style="width: 40px; height: 40px; transition: all 0.3s ease;">
                        <span>4</span>
                    </div>
                    <small class="fw-bold">Review</small>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

### 12.3 Real-Time Validation Feedback

**Inline Form Validation with Animation:**

```html
<div class="mb-3">
    <label for="phone" class="form-label">Phone Number</label>
    <input type="tel"
           class="form-control"
           id="phone"
           name="phone"
           pattern="[0-9]{10,11}"
           oninput="validatePhone(this)"
           required>

    <!-- Validation feedback (hidden by default) -->
    <div class="invalid-feedback" style="display: none;">
        <i class="bi bi-exclamation-circle"></i> Please enter a valid 10-11 digit phone number.
    </div>
    <div class="valid-feedback" style="display: none;">
        <i class="bi bi-check-circle"></i> Valid phone number.
    </div>
</div>

<script>
function validatePhone(input) {
    const value = input.value;
    const pattern = /^[0-9]{10,11}$/;
    const isValid = pattern.test(value);

    const invalidFeedback = input.nextElementSibling;
    const validFeedback = invalidFeedback.nextElementSibling;

    if (value.length === 0) {
        // No input yet - neutral state
        input.classList.remove('is-valid', 'is-invalid');
        invalidFeedback.style.display = 'none';
        validFeedback.style.display = 'none';
    } else if (isValid) {
        // Valid input - show success with animation
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        invalidFeedback.style.display = 'none';
        validFeedback.style.display = 'block';
        validFeedback.style.animation = 'fadeIn 0.3s ease';
    } else {
        // Invalid input - show error with shake animation
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        validFeedback.style.display = 'none';
        invalidFeedback.style.display = 'block';
        invalidFeedback.style.animation = 'shake 0.3s ease';
    }
}
</script>

<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-5px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.form-control.is-valid {
    border-color: #198754;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%23198754' d='M2.3 6.73L.6 4.53c-.4-1.04.46-1.4 1.1-.8l1.1 1.4 3.4-3.8c.6-.63 1.6-.27 1.2.7l-4 4.6c-.43.5-.8.4-1.1.1z'/%3e%3c/svg%3e");
}

.form-control.is-invalid {
    border-color: #dc3545;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23dc3545'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
}
</style>
```

---

### 12.4 Skeleton Loaders for Medical Data

**Loading Placeholder for Patient Cards:**

```html
<!-- Skeleton loader while fetching patient data -->
<div class="card shadow-sm mb-3 skeleton-loader" aria-busy="true" aria-label="Loading patient data">
    <div class="card-body">
        <div class="d-flex align-items-center">
            <div class="skeleton skeleton-circle me-3" style="width: 60px; height: 60px;"></div>
            <div class="flex-grow-1">
                <div class="skeleton skeleton-text mb-2" style="width: 60%;"></div>
                <div class="skeleton skeleton-text" style="width: 40%;"></div>
            </div>
        </div>
    </div>
</div>

<style>
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}

.skeleton-circle {
    border-radius: 50%;
}

.skeleton-text {
    height: 16px;
    border-radius: 4px;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
</style>
```

---

## Reference Documentation

**See also:**
- `UI_UX_DESIGN_SYSTEM.md` - Complete design system documentation
- `templates/components/` - Reusable component library
- `common/widgets.py` - Bootstrap widget library
- `.claude/ANNOUNCEMENTS_MODULE_DEMO.md` - Example implementation

---

## Enforcement

**This skill is MANDATORY for all UI work.**

When reviewing templates, if you see:
- Fixed widths → REFACTOR to use responsive classes
- Missing viewport meta → ADD immediately
- Unwrapped tables → WRAP in `table-responsive`
- Tiny buttons on mobile → USE `btn-lg` or ensure 44x44px minimum
- Non-responsive images → ADD `img-fluid` class
- Hardcoded colors → USE Bootstrap color classes
- No hamburger menu → ADD `navbar-toggler`

**No exceptions.** All UI must be mobile-first and follow the design system.

---

**Last Updated:** 2025-11-23
**Status:** ⭐ MANDATORY
**Coverage:** 100% of all templates and UI components
**Breakpoints:** xs, sm, md, lg, xl, xxl
**Accessibility:** WCAG 2.1 AA compliant

**Mobile-first design system ensures beautiful, accessible, responsive experiences on ALL devices.**
