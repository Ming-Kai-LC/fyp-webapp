---
name: UI/UX Consistency
description: Enforces consistent UI/UX design system across all modules using Bootstrap 5. Auto-applies design patterns, color schemes, and component styles for COVID-19 Detection webapp.
---

Maintains consistent design language, patterns, and user experience throughout the application.

## Design System

### Color Palette (Bootstrap 5 Extended)
```css
Primary:   #0d6efd (Blue - main actions)
Secondary: #6c757d (Gray - secondary actions)
Success:   #198754 (Green - COVID negative, success states)
Danger:    #dc3545 (Red - COVID positive, errors)
Warning:   #ffc107 (Yellow - pending validation)
Info:      #0dcaf0 (Cyan - informational)
Light:     #f8f9fa (Backgrounds)
Dark:      #212529 (Text)
```

### Typography Scale
- **Display**: `display-1` to `display-6` for hero sections
- **Headings**: `h1` to `h6` (or classes for semantic HTML)
- **Body**: Default 16px, `lead` for emphasis
- **Small**: `small` class or `text-muted` for secondary info

### Spacing System
Follow Bootstrap's spacing scale (0-5):
- **0**: 0
- **1**: 0.25rem (4px)
- **2**: 0.5rem (8px)
- **3**: 1rem (16px)
- **4**: 1.5rem (24px)
- **5**: 3rem (48px)

## Component Patterns

### Cards (Consistent Structure)
```html
<div class="card shadow-sm">
    <div class="card-header bg-primary text-white">
        <h5 class="mb-0"><i class="bi bi-icon"></i> Title</h5>
    </div>
    <div class="card-body">
        <!-- Content -->
    </div>
    <div class="card-footer text-muted">
        <!-- Optional footer -->
    </div>
</div>
```

### Buttons (Consistent Sizing & Icons)
```html
<!-- Primary action -->
<button class="btn btn-primary">
    <i class="bi bi-check-circle"></i> Submit
</button>

<!-- Secondary action -->
<button class="btn btn-outline-primary">
    <i class="bi bi-arrow-left"></i> Back
</button>

<!-- Destructive action -->
<button class="btn btn-danger">
    <i class="bi bi-trash"></i> Delete
</button>
```

### Forms (Consistent Layout)
```html
<form method="post">
    {% csrf_token %}

    <div class="mb-3">
        <label for="id_field" class="form-label">Field Label</label>
        <input type="text" class="form-control" id="id_field" name="field">
        <div class="form-text">Help text here</div>
    </div>

    <div class="mb-3">
        <button type="submit" class="btn btn-primary w-100">
            <i class="bi bi-save"></i> Save
        </button>
    </div>
</form>
```

### Tables (Consistent Styling)
```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data</td>
                <td>Data</td>
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

### Badges (Status Indicators)
```html
<!-- COVID Positive -->
<span class="badge bg-danger">COVID</span>

<!-- Normal -->
<span class="badge bg-success">Normal</span>

<!-- Pending -->
<span class="badge bg-warning text-dark">Pending</span>

<!-- Validated -->
<span class="badge bg-success"><i class="bi bi-check-circle"></i> Validated</span>
```

### Alerts (User Feedback)
```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
    <i class="bi bi-check-circle-fill"></i> Success message
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
```

## Icon Usage (Bootstrap Icons)

**Consistent icon mapping:**
- Upload: `bi-cloud-upload`
- View/Results: `bi-eye`
- Explainability: `bi-lightbulb`
- Dashboard: `bi-speedometer2`
- User: `bi-person-circle`
- Doctor: `bi-hospital`
- Patient: `bi-person`
- Admin: `bi-gear`
- COVID: `bi-shield-exclamation`
- Success: `bi-check-circle`
- Error: `bi-x-circle`
- History: `bi-clock-history`
- Settings: `bi-gear`
- Logout: `bi-box-arrow-right`
- Login: `bi-box-arrow-in-right`

## Navigation Patterns

### Breadcrumbs (For Deep Pages)
```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/">Home</a></li>
        <li class="breadcrumb-item"><a href="/detection/">Detection</a></li>
        <li class="breadcrumb-item active">Results</li>
    </ol>
</nav>
```

### Consistent Page Headers
```html
<div class="row mb-4">
    <div class="col">
        <h2><i class="bi bi-icon"></i> Page Title</h2>
        <p class="text-muted">Brief description</p>
    </div>
</div>
```

## User Feedback Patterns

### Loading States
```html
<div class="text-center py-5">
    <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
    <p class="mt-2 text-muted">Analyzing X-ray with AI models...</p>
</div>
```

### Empty States
```html
<div class="text-center py-5">
    <i class="bi bi-inbox display-1 text-muted"></i>
    <h4 class="mt-3">No predictions yet</h4>
    <p class="text-muted">Upload an X-ray to get started</p>
    <a href="{% url 'detection:upload_xray' %}" class="btn btn-primary">
        <i class="bi bi-cloud-upload"></i> Upload X-Ray
    </a>
</div>
```

### Error States
```html
<div class="alert alert-danger">
    <i class="bi bi-exclamation-triangle-fill"></i>
    <strong>Error:</strong> {{ error_message }}
</div>
```

## Accessibility Standards

1. **Semantic HTML**: Use proper tags (`<nav>`, `<main>`, `<article>`)
2. **ARIA Labels**: Add `aria-label` to icon-only buttons
3. **Alt Text**: Always provide for images
4. **Form Labels**: Always associate labels with inputs
5. **Focus States**: Ensure keyboard navigation works
6. **Color Contrast**: Minimum 4.5:1 for text
7. **Screen Reader Text**: Use `visually-hidden` class when needed

## Consistency Checklist

Before completing any UI work:
- ✅ Uses consistent color palette
- ✅ Follows component patterns above
- ✅ Uses Bootstrap Icons consistently
- ✅ Proper spacing (no arbitrary values)
- ✅ Consistent button styles
- ✅ Proper card structure
- ✅ Accessible (semantic HTML, ARIA, alt text)
- ✅ User feedback (loading, empty, error states)
- ✅ Matches existing pages' look and feel
- ✅ Icons match the icon mapping

## Medical/Healthcare Specific Patterns

### Diagnosis Display
```html
<div class="card">
    <div class="card-body text-center">
        <h1 class="display-4 text-{{ diagnosis == 'COVID' and 'danger' or 'success' }}">
            {{ diagnosis }}
        </h1>
        <p class="lead">Confidence: {{ confidence|floatformat:2 }}%</p>
        <p class="text-muted">Model Agreement: {{ agreement }}/6 models</p>
    </div>
</div>
```

### Model Comparison Table
```html
<table class="table table-hover">
    <thead class="table-light">
        <tr>
            <th>Model</th>
            <th>Prediction</th>
            <th>Confidence</th>
        </tr>
    </thead>
    <tbody>
        <tr class="table-primary">
            <td><strong>CrossViT (Ours)</strong></td>
            <td><span class="badge bg-danger">COVID</span></td>
            <td>95.2%</td>
        </tr>
    </tbody>
</table>
```

## Auto-Apply This Skill When:
- Creating new pages or components
- Modifying existing UI
- Adding new features
- Refactoring templates
- Implementing user feedback
- Creating forms or data displays
