---
name: Standard Folder Structure
description: Enforces consistent folder structure across all Django modules. Auto-applies when creating new modules or organizing files to ensure clean, maintainable project structure.
---

# Standard Folder Structure

Ensures all modules in the COVID-19 Detection webapp follow a consistent, clean folder structure.

## Project Root Structure

```
fyp-webapp/
├── .claude/                    # Claude Code configuration
│   └── skills/                 # Auto-applying skills
│       ├── mobile-responsive/
│       ├── django-module-creation/
│       ├── ui-ux-consistency/
│       ├── security-best-practices/
│       ├── performance-optimization/
│       ├── code-quality-standards/
│       ├── component-reusability/
│       └── standard-folder-structure/
│
├── config/                     # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   ├── images/
│   └── ml_models/              # ML model weights (.pth files)
│
├── media/                      # User-uploaded files
│   ├── xrays/
│   │   ├── original/
│   │   ├── processed/
│   │   └── heatmaps/
│   └── exports/
│
├── templates/                  # Global templates
│   ├── base.html
│   ├── home.html
│   ├── components/             # Reusable components
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   ├── messages.html
│   │   ├── card.html
│   │   ├── empty_state.html
│   │   ├── loading.html
│   │   └── pagination.html
│   └── layouts/                # Page layouts
│       ├── dashboard_base.html
│       └── auth_base.html
│
├── docs/                       # Documentation
│   ├── MODULE_DEVELOPMENT_GUIDE.md
│   ├── PROJECT_STRUCTURE.md
│   ├── SESSION_HANDOFF_TEMPLATE.md
│   ├── VALIDATION_CHECKLIST.md
│   ├── TRACKING.md             # Progress tracking
│   └── sessions/               # Session handoffs
│       └── session_YYYYMMDD_name.md
│
├── [module_name]/             # Django app (Standard Module Structure)
│   ├── __init__.py
│   ├── models.py              # Database models
│   ├── views.py               # View classes
│   ├── forms.py               # Form classes
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin configuration
│   ├── services.py            # Business logic layer
│   ├── managers.py            # Custom model managers
│   ├── mixins.py              # Reusable view mixins
│   ├── validators.py          # Custom validators
│   ├── signals.py             # Django signals
│   ├── apps.py                # App configuration
│   │
│   ├── templates/             # Module templates
│   │   └── [module_name]/
│   │       ├── components/    # Module-specific components
│   │       └── pages/         # Module pages
│   │
│   ├── static/                # Module static files
│   │   └── [module_name]/
│   │       ├── css/
│   │       ├── js/
│   │       └── images/
│   │
│   ├── templatetags/          # Custom template tags
│   │   └── [module_name]_tags.py
│   │
│   ├── management/            # Management commands
│   │   └── commands/
│   │       └── [command_name].py
│   │
│   ├── migrations/            # Database migrations
│   │   └── 0001_initial.py
│   │
│   └── tests/                 # Module tests
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       ├── test_forms.py
│       ├── test_services.py
│       ├── factories.py
│       └── fixtures/
│
├── tests/                     # Project-wide tests
│   ├── integration/
│   ├── e2e/
│   └── performance/
│
├── scripts/                   # Utility scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
│
├── logs/                      # Application logs (gitignored)
│   ├── django.log
│   ├── ml_inference.log
│   └── security.log
│
├── requirements/              # Python dependencies
│   ├── base.txt              # Common dependencies
│   ├── development.txt       # Development only
│   └── production.txt        # Production only
│
├── .env.example              # Environment variables template
├── .gitignore
├── manage.py
├── README.md
└── pytest.ini
```

## Standard Module Structure

When creating a new module, use this template:

```
[module_name]/
├── __init__.py
├── models.py              # Fat models - business logic here
├── views.py               # Thin views - use CBVs
├── forms.py               # All forms
├── urls.py                # URL patterns
├── admin.py               # Admin interface
├── services.py            # Service layer (complex operations)
├── managers.py            # Custom querysets
├── mixins.py              # Reusable view mixins
├── validators.py          # Custom field validators
├── signals.py             # Signal handlers
├── apps.py                # App configuration
│
├── templates/
│   └── [module_name]/
│       ├── components/    # Reusable components
│       │   ├── [module]_card.html
│       │   ├── [module]_form.html
│       │   └── [module]_table.html
│       └── pages/         # Full pages
│           ├── list.html
│           ├── detail.html
│           ├── create.html
│           └── update.html
│
├── static/
│   └── [module_name]/
│       ├── css/
│       │   └── [module].css
│       ├── js/
│       │   └── [module].js
│       └── images/
│
├── templatetags/
│   └── [module_name]_tags.py
│
├── management/
│   └── commands/
│       └── [custom_command].py
│
├── migrations/
│   └── 0001_initial.py
│
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    ├── test_forms.py
    ├── test_services.py
    ├── factories.py
    └── fixtures/
```

## File Organization Rules

### 1. Models (models.py)
- One model per class
- Related models in same file
- Abstract base models at the top
- Use `class Meta` for options
- Maximum 500 lines per file; split if larger

### 2. Views (views.py)
- Group related views together
- Use class-based views (CBVs)
- One view class per operation
- Maximum 500 lines; create views/ package if needed:
  ```
  views/
  ├── __init__.py
  ├── dashboard.py
  ├── upload.py
  └── results.py
  ```

### 3. Forms (forms.py)
- One form per class
- Model forms together
- Regular forms together
- Custom widgets in separate file if complex

### 4. Services (services.py)
- Business logic outside of views/models
- Static methods for stateless operations
- Class methods for reusable logic
- Split into services/ package if > 500 lines

### 5. Templates
- **components/**: Reusable snippets (< 50 lines each)
- **pages/**: Full pages that extend layouts
- Never exceed 300 lines per template
- Use includes for repeated sections

### 6. Static Files
- Module-specific CSS/JS in module's static folder
- Global CSS/JS in root static folder
- Use meaningful names: `detection-upload.js`, not `script.js`

### 7. Tests
- One test file per module file
- `test_models.py` for models.py
- Use factories for test data
- Group tests by feature

## Naming Conventions

### Files
- `snake_case.py` for Python files
- `kebab-case.html` for templates
- `kebab-case.css` and `kebab-case.js` for assets

### Directories
- `snake_case/` for Python packages
- `kebab-case/` for template directories

### Templates
- `list.html` - List view
- `detail.html` - Detail view
- `create.html` - Create form
- `update.html` - Update form
- `delete.html` - Delete confirmation
- `[feature]_card.html` - Card component
- `[feature]_form.html` - Form component

## When to Create New Files vs. Extend Existing

### Create New File When:
- File exceeds 500 lines
- Adding completely new feature
- Logic is independent

### Extend Existing File When:
- Closely related functionality
- File under 300 lines
- Shares many dependencies

## Module Package Structure (for large modules)

If a module grows large (> 1000 lines), convert to package:

```
[module_name]/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── core.py
│   ├── prediction.py
│   └── patient.py
├── views/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── upload.py
│   └── results.py
├── forms/
│   ├── __init__.py
│   ├── upload.py
│   └── registration.py
├── services/
│   ├── __init__.py
│   ├── prediction.py
│   └── ml_engine.py
└── ...
```

## Checklist for New Modules

Before creating a new module:
- ✅ Plan folder structure
- ✅ Create all standard directories
- ✅ Add `__init__.py` to make packages
- ✅ Create empty test files
- ✅ Add module to `INSTALLED_APPS`
- ✅ Create URL patterns
- ✅ Document in PROJECT_STRUCTURE.md

## Checklist for File Organization

Before committing:
- ✅ No file exceeds 500 lines
- ✅ Related code is grouped together
- ✅ Imports are organized (stdlib, Django, third-party, local)
- ✅ Templates use components/ for reusable parts
- ✅ Static files in correct module folder
- ✅ Tests mirror source structure
- ✅ All directories have appropriate `__init__.py`

## Auto-Apply This Skill When:
- Creating new Django modules
- Adding new features
- Organizing files
- Refactoring code
- Creating templates
- Adding static files
- Writing tests
- Reviewing code structure
