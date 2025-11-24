---
name: Mobile-Responsive Design
description: Ensures all UI components are mobile-first and responsive across all devices using Bootstrap 5. Auto-applies responsive design patterns when creating templates, forms, dashboards, and navigation.
---

# Mobile-Responsive Design

Ensures all UI components are mobile-first and responsive across all devices for the COVID-19 Detection webapp.

## Core Principles

1. **Mobile-First Approach**: Design for mobile, then scale up
2. **Bootstrap 5 Grid System**: Use responsive grid classes
3. **Breakpoint Testing**: Test at all Bootstrap breakpoints (xs, sm, md, lg, xl, xxl)
4. **Touch-Friendly**: Minimum 44x44px touch targets
5. **Responsive Images**: Use responsive image classes

## Guidelines

### Bootstrap 5 Responsive Classes
- Use `col-12 col-md-6 col-lg-4` pattern for columns
- Use responsive utility classes: `d-none d-md-block`, `text-center text-md-start`
- Use `container` or `container-fluid` for proper padding

### Required Meta Tags
Every template must include:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Responsive Navigation
- Use Bootstrap navbar with `navbar-expand-lg`
- Hamburger menu for mobile
- Collapsible sections for smaller screens

### Responsive Tables
Always wrap tables:
```html
<div class="table-responsive">
    <table class="table">...</table>
</div>
```

### Responsive Images
```html
<img src="..." class="img-fluid" alt="...">
```

### Responsive Typography
- Use Bootstrap responsive font sizes: `fs-1` to `fs-6`
- Use `lead` class for introductory text
- Ensure text is readable at 16px minimum

### Responsive Spacing
- Use responsive margin/padding: `mt-3 mt-md-5`
- Adjust spacing for different screen sizes

### Form Layouts
- Stack form fields on mobile
- Use `row` and `col` for larger screens
- Ensure labels are above inputs on mobile

## Testing Checklist

Before completing any UI task, verify:
- ✅ Looks good on mobile (375px - iPhone SE)
- ✅ Looks good on tablet (768px - iPad)
- ✅ Looks good on desktop (1920px)
- ✅ Navigation works on all sizes
- ✅ Images scale properly
- ✅ Text is readable
- ✅ No horizontal scrolling
- ✅ Touch targets are large enough
- ✅ Forms are usable on mobile

## Common Mobile Issues to Avoid

1. **Fixed widths** - Use `w-100` or percentages instead
2. **Tiny buttons** - Minimum size: `btn btn-lg` on mobile
3. **Horizontal scrolling** - Always use `container` or `overflow-hidden`
4. **Unreadable text** - Minimum 16px font size
5. **Overlapping elements** - Test at all breakpoints
6. **Missing hamburger menu** - Always include for mobile nav
7. **Non-responsive cards** - Use Bootstrap card grid system

## Example Pattern

```html
<!-- Mobile-first responsive card grid -->
<div class="container">
    <div class="row g-4">
        <div class="col-12 col-sm-6 col-md-4 col-lg-3">
            <div class="card h-100">
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

## Auto-Apply This Skill When:
- Creating new templates
- Modifying existing UI
- Adding forms or tables
- Creating dashboards
- Designing card layouts
- Building navigation
