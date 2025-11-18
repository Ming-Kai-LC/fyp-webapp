# Module Validation Checklist

**Use this checklist before committing any new module or major feature**

---

## 🔍 Pre-Commit Validation

### 1. Code Quality ✅

#### Python Code Standards
- [ ] All code follows PEP 8 style guide
- [ ] No unused imports or variables
- [ ] No commented-out code (remove or document why)
- [ ] Type hints added to all public functions
- [ ] Docstrings for all classes and methods (Google style)
- [ ] No print statements (use logging instead)
- [ ] No hardcoded values (use settings or constants)

#### Django-Specific
- [ ] Models inherit from appropriate base classes
- [ ] Views use mixins for common functionality
- [ ] Business logic in services, not views
- [ ] QuerySets optimized (no N+1 queries)
- [ ] Signals used appropriately (if needed)

#### Import Organization
```python
# Standard library
import os
from typing import Optional

# Django
from django.db import models

# Third-party
import requests

# Local
from .models import MyModel
```
- [ ] Imports organized in correct order
- [ ] No circular imports

---

### 2. Functionality ⚙️

#### Models
- [ ] All fields have appropriate types
- [ ] All fields have help_text
- [ ] Foreign keys have related_name
- [ ] Proper indexes on filtered fields
- [ ] __str__ method returns meaningful string
- [ ] Custom methods documented
- [ ] Validators added where needed

#### Views
- [ ] Authentication required where needed
- [ ] Authorization checks implemented (role-based)
- [ ] Proper HTTP methods used
- [ ] Error handling implemented
- [ ] Success messages added
- [ ] Redirects to appropriate pages
- [ ] Context includes all needed data

#### Forms
- [ ] All fields validated
- [ ] Clean methods for complex validation
- [ ] Widget attributes include Bootstrap classes
- [ ] Help text provided
- [ ] Error messages user-friendly
- [ ] CSRF token included in templates

#### Admin
- [ ] list_display configured
- [ ] list_filter for common filters
- [ ] search_fields for searchable fields
- [ ] Appropriate fields read-only
- [ ] Custom admin methods if needed

---

### 3. Security 🔒

#### Authentication & Authorization
- [ ] LoginRequiredMixin used on protected views
- [ ] Role-based access control implemented
- [ ] Object-level permissions checked
- [ ] Rate limiting on sensitive endpoints (if applicable)

#### Input Validation
- [ ] All user inputs validated
- [ ] File uploads validated (type, size, content)
- [ ] SQL injection prevented (using ORM)
- [ ] XSS prevented (template auto-escaping)
- [ ] Command injection prevented (avoid shell=True)

#### Data Protection
- [ ] Sensitive data encrypted (if applicable)
- [ ] Passwords hashed (Django handles this)
- [ ] CSRF tokens on all forms
- [ ] No secrets in code (use environment variables)

#### Security Headers
- [ ] X-Frame-Options set
- [ ] X-Content-Type-Options set
- [ ] Content-Security-Policy configured (if needed)

---

### 4. Performance ⚡

#### Database Queries
- [ ] select_related() used for ForeignKey/OneToOne
- [ ] prefetch_related() used for ManyToMany/Reverse FK
- [ ] only() or defer() used for large tables
- [ ] Database indexes on filtered fields
- [ ] Bulk operations used when appropriate
- [ ] No queries in templates (prefetch in view)

#### Caching
- [ ] Expensive operations cached
- [ ] Cache invalidation implemented
- [ ] Cache keys unique and descriptive

#### Assets
- [ ] Static files collected
- [ ] Images optimized
- [ ] CSS/JS minified (in production)
- [ ] CDN used for external resources

#### ML/AI (if applicable)
- [ ] Models loaded efficiently
- [ ] VRAM managed (clear cache)
- [ ] Batch processing optimized
- [ ] Mixed precision used

---

### 5. UI/UX 🎨

#### Mobile Responsive
- [ ] Tested on mobile (375px - iPhone SE)
- [ ] Tested on tablet (768px - iPad)
- [ ] Tested on desktop (1920px)
- [ ] No horizontal scrolling
- [ ] Touch targets ≥ 44x44px
- [ ] Hamburger menu works

#### Design Consistency
- [ ] Uses Bootstrap 5 components
- [ ] Colors match design system
- [ ] Icons from Bootstrap Icons
- [ ] Consistent spacing (Bootstrap classes)
- [ ] Typography follows scale
- [ ] Buttons consistent style

#### User Feedback
- [ ] Loading states shown
- [ ] Empty states shown
- [ ] Error states shown
- [ ] Success messages displayed
- [ ] Form validation feedback clear

#### Accessibility
- [ ] Semantic HTML used
- [ ] Alt text on images
- [ ] Labels associated with inputs
- [ ] ARIA labels on icon buttons
- [ ] Keyboard navigation works
- [ ] Color contrast meets WCAG 2.1

---

### 6. Testing ✅

#### Test Coverage
- [ ] Model tests written (CRUD operations)
- [ ] View tests written (GET/POST)
- [ ] Form tests written (validation)
- [ ] Service tests written (business logic)
- [ ] Test coverage ≥ 80%
- [ ] All tests passing

#### Test Quality
- [ ] Tests are independent
- [ ] Tests use factories
- [ ] Test names descriptive
- [ ] Edge cases covered
- [ ] Error conditions tested

#### Manual Testing
- [ ] Feature tested in browser
- [ ] Different user roles tested
- [ ] Error scenarios tested
- [ ] Edge cases verified

---

### 7. Documentation 📚

#### Code Documentation
- [ ] Module docstring explains purpose
- [ ] Class docstrings include attributes and examples
- [ ] Method docstrings (Args, Returns, Raises)
- [ ] Complex logic has comments
- [ ] README updated (if needed)

#### Project Documentation
- [ ] MODULE_DEVELOPMENT_GUIDE.md updated
- [ ] PROJECT_STRUCTURE.md updated
- [ ] TESTING_GUIDE.md updated (if needed)
- [ ] Session handoff created

#### User Documentation
- [ ] Admin panel help text
- [ ] Form field help text
- [ ] User guide updated (if applicable)

---

### 8. Integration 🔗

#### URL Configuration
- [ ] URLs registered in config/urls.py
- [ ] app_name set in app's urls.py
- [ ] URL patterns follow conventions
- [ ] Named URLs used in templates

#### Navigation
- [ ] Links added to navbar (if needed)
- [ ] Breadcrumbs added (if deep pages)
- [ ] "Back" buttons work correctly
- [ ] Active nav highlighting works

#### Cross-Module Integration
- [ ] Dependencies documented
- [ ] Imports work correctly
- [ ] No circular dependencies
- [ ] Signals connected (if needed)

---

### 9. Database 🗄️

#### Migrations
- [ ] Migrations created (makemigrations)
- [ ] Migrations applied (migrate)
- [ ] No migration conflicts
- [ ] Migration files added to git

#### Data Integrity
- [ ] Foreign keys have on_delete set
- [ ] Required fields not null
- [ ] Unique constraints where needed
- [ ] Default values appropriate

---

### 10. Skills Application 🎯

#### Auto-Applied Skills
- [ ] mobile-responsive verified
- [ ] ui-ux-consistency verified
- [ ] django-module-creation patterns followed
- [ ] security-best-practices applied
- [ ] performance-optimization implemented
- [ ] code-quality-standards met
- [ ] component-reusability maximized

---

## 🎯 Module-Specific Checks

### For CRUD Modules
- [ ] List view with pagination
- [ ] Detail view
- [ ] Create/Update forms
- [ ] Delete confirmation
- [ ] Filtering/search functionality

### For Dashboard Modules
- [ ] Statistics accurate
- [ ] Charts render correctly
- [ ] Date ranges work
- [ ] Export functionality
- [ ] Data cached appropriately

### For File Upload Modules
- [ ] File type validation
- [ ] File size limits
- [ ] Malware scanning (if critical)
- [ ] Storage path secure
- [ ] Thumbnails generated (if images)

### For API Modules
- [ ] Authentication required
- [ ] Permissions checked
- [ ] Rate limiting applied
- [ ] Pagination implemented
- [ ] API documentation

---

## ✅ Final Checks

### Before Commit
```bash
# Run these commands:
python manage.py check
python manage.py test
python manage.py makemigrations --dry-run
flake8 module_name/
black --check module_name/
```

- [ ] No errors in `python manage.py check`
- [ ] All tests pass
- [ ] No pending migrations
- [ ] No linting errors
- [ ] Code formatted with black

### Git
- [ ] All changes staged
- [ ] Commit message descriptive
- [ ] No sensitive data in commit
- [ ] Branch is correct

### Documentation
- [ ] Session handoff completed
- [ ] All guides updated
- [ ] Comments clear and helpful

---

## 📊 Validation Score

**Category** | **Completed** | **Total** | **Score**
------------ | ------------- | --------- | ---------
Code Quality | __ / 15 | 15 | __%
Functionality | __ / 22 | 22 | __%
Security | __ / 13 | 13 | __%
Performance | __ / 12 | 12 | __%
UI/UX | __ / 19 | 19 | __%
Testing | __ / 11 | 11 | __%
Documentation | __ / 12 | 12 | __%
Integration | __ / 10 | 10 | __%
Database | __ / 8 | 8 | __%
Skills | __ / 7 | 7 | __%

**Overall Score: __ / 129 (__ %)**

### Pass Criteria
- **Critical Features:** 100% (Security, Functionality core)
- **High Priority:** ≥ 90% (Performance, Testing, UI/UX)
- **Medium Priority:** ≥ 80% (Code Quality, Documentation)
- **Nice to Have:** ≥ 70% (Advanced features)

---

## 🚨 Blockers

If any critical items are not checked, document why:

**Item:** [Checklist item not completed]
**Reason:** [Why it's not done]
**Plan:** [When/how it will be addressed]
**Impact:** [Risk if not addressed]

---

## ✅ Sign-Off

**Module Name:** _________________
**Date:** _________________
**Validated By:** _________________
**Ready for Commit:** ✅ Yes / ❌ No

**Notes:**
[Any additional notes or considerations]

---

**Use this checklist consistently to maintain high quality across all modules!**
