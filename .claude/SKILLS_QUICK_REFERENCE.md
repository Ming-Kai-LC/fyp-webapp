# Skills Quick Reference Guide

**Version:** 2.0.0
**Last Updated:** 2025-11-23
**Total Skills:** 16

Quick lookup guide for all Claude Code skills.

---

## ⚡ Quick Lookup by Task

### Creating a New Module
**Skills Applied:** module-creation-lifecycle, foundation-components, standard-folder-structure
**Priority:** ⭐⭐⭐ CRITICAL

### Creating a Form
**Skills Applied:** foundation-components (widgets), security-best-practices, ui-ux-consistency
**Key Rule:** ALWAYS use `common.widgets`, NEVER hardcode Bootstrap classes

### Creating a Model
**Skills Applied:** foundation-components (base models), django-module-creation
**Key Rule:** ALWAYS inherit from `TimeStampedModel` minimum

### Creating a Template
**Skills Applied:** foundation-components (tags/components), mobile-responsive, ui-ux-consistency
**Key Rule:** ALWAYS `{% load common_tags %}`, use `{% include 'components/...' %}`

### Adding Validation
**Skills Applied:** foundation-components (utils), security-best-practices
**Key Rule:** Use `common.utils` functions, never reimplement

### Implementing Permissions
**Skills Applied:** user-role-permissions, foundation-components (decorators)
**Key Rule:** Use `@staff_required`, never manual permission checks

### Writing Business Logic
**Skills Applied:** three-tier-architecture, full-stack-django-patterns
**Key Rule:** Complex workflows → Service layer

### Committing Code
**Skills Applied:** development-workflow, testing-automation
**Key Rule:** Conventional Commits format, pre-commit hooks run automatically

---

## 📚 All Skills (Alphabetical)

| # | Skill | Tier | Priority | File |
|---|-------|------|----------|------|
| 1 | code-quality-standards | 3 | Standard | `code-quality-standards/skill.md` |
| 2 | component-reusability | 3 | Standard | `component-reusability/skill.md` |
| 3 | development-workflow | 2 | ⭐ VERSION CONTROL | `development-workflow/skill.md` |
| 4 | django-module-creation | 3 | Standard | `django-module-creation/skill.md` |
| 5 | **foundation-components** | 1 | ⭐ CRITICAL | `foundation-components/skill.md` |
| 6 | **full-stack-django-patterns** | 1 | ⭐ COMPREHENSIVE | `full-stack-django-patterns/skill.md` |
| 7 | mobile-responsive | 3 | Standard | `mobile-responsive/skill.md` |
| 8 | module-creation-lifecycle | 2 | ⭐ LIFECYCLE | `module-creation-lifecycle/skill.md` |
| 9 | performance-optimization | 3 | Standard | `performance-optimization/skill.md` |
| 10 | security-best-practices | 3 | Standard | `security-best-practices/skill.md` |
| 11 | standard-folder-structure | 3 | Standard | `standard-folder-structure/skill.md` |
| 12 | testing-automation | 2 | ⭐ QUALITY | `testing-automation/skill.md` |
| 13 | three-tier-architecture | 2 | ⭐ ARCHITECTURAL | `three-tier-architecture/skill.md` |
| 14 | ui-ux-consistency | 3 | Standard | `ui-ux-consistency/skill.md` |
| 15 | **user-role-permissions** | 1 | ⭐ PRIMARY | `user-role-permissions/skill.md` |
| 16 | virtual-environment | 3 | Standard | `virtual-environment/skill.md` |

---

## 🌟 Tier 1: Foundation (Must Use)

### foundation-components ⭐ CRITICAL
**Use for:** ALL code (models, forms, templates, views)
**Provides:** Base models, widgets, tags, components, utils, decorators
**Result:** 20-30% code reduction

### user-role-permissions ⭐ PRIMARY
**Use for:** All auth/authorization
**Enforces:** 3 user roles (admin, staff, patient)

### full-stack-django-patterns ⭐ COMPREHENSIVE
**Use for:** All Django development
**Provides:** 15 comprehensive pattern sections

---

## 🏗️ Tier 2: Architecture & Lifecycle

### three-tier-architecture ⭐ ARCHITECTURAL
**Use for:** Complex workflows, API/web code sharing
**Result:** 30-50% view complexity reduction

### module-creation-lifecycle ⭐ LIFECYCLE
**Use for:** Creating new modules/apps
**Phases:** Planning → Code → Quality → Integration

### testing-automation ⭐ QUALITY
**Use for:** All code, commits, PRs
**Levels:** Pre-commit → CI/CD → Test generation → Coverage

### development-workflow ⭐ VERSION CONTROL
**Use for:** Git commits, PRs, code reviews
**Format:** Conventional Commits

---

## 🔧 Tier 3: Best Practices

- **django-module-creation:** Django OOP patterns
- **security-best-practices:** OWASP + Healthcare security
- **performance-optimization:** Database + ML optimization
- **code-quality-standards:** PEP 8 + Testing
- **component-reusability:** DRY principles
- **standard-folder-structure:** Folder organization
- **mobile-responsive:** Mobile-first design
- **ui-ux-consistency:** Design system
- **virtual-environment:** Python venv enforcement

---

## 🎯 Foundation Components Checklist

**Before committing ANY module:**

### Models ✅
- [ ] Inherits from `TimeStampedModel` (or FullAuditModel)
- [ ] NO manual `created_at`/`updated_at` fields
- [ ] Type hints on all methods

### Forms ✅
- [ ] Uses `common.widgets` for ALL fields
- [ ] NO hardcoded `attrs={'class': 'form-control'}`
- [ ] Validation uses `common.utils`

### Views ✅
- [ ] Uses permission decorators (`@staff_required`)
- [ ] NO manual permission checks
- [ ] Thin views (<50 lines)

### Templates ✅
- [ ] Loads `{% load common_tags %}`
- [ ] Uses `{% include 'components/card.html' %}`
- [ ] Uses `{% status_badge %}`, `{% format_datetime %}`
- [ ] NO duplicated HTML

---

## 📖 Common Commands

### Check skill structure
```bash
find .claude/skills -name "skill.md" -type f
```

### View skill README
```bash
cat .claude/skills/README.md
```

### Check for old SKILL.md files
```bash
find .claude/skills -name "SKILL.md" -type f
# Should return 0 files
```

---

## 🔗 Related Documentation

- **Skills Overview:** `.claude/skills/README.md` (700+ lines, v2.0.0)
- **Main Project Rules:** `.claude/CLAUDE.md`
- **Refactoring Summary:** `.claude/SKILLS_REFACTORING_SUMMARY.md`
- **UI/UX Design System:** `UI_UX_DESIGN_SYSTEM.md`
- **Foundation Test Results:** `.claude/FOUNDATION_TEST_RESULTS.md`
- **Announcements Demo:** `.claude/ANNOUNCEMENTS_MODULE_DEMO.md`

---

## 🚨 Critical Rules (Never Violate)

1. **ALWAYS** inherit models from `TimeStampedModel`
2. **NEVER** hardcode Bootstrap classes in forms
3. **ALWAYS** use `common.widgets` for form fields
4. **ALWAYS** `{% load common_tags %}` in templates
5. **NEVER** duplicate card/alert HTML (use components)
6. **ALWAYS** use permission decorators, never manual checks
7. **ALWAYS** use `common.utils` for validation
8. **NEVER** reimplement validation logic

**Violation = Refactor immediately**

---

## ⚡ Quick Fixes for Common Mistakes

### ❌ Hardcoded Bootstrap Class
```python
# WRONG
'title': forms.TextInput(attrs={'class': 'form-control'})
```
**Fix:** Use `BootstrapTextInput()`

### ❌ Manual Timestamps
```python
# WRONG
class MyModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
```
**Fix:** Inherit from `TimeStampedModel`

### ❌ Manual Permission Check
```python
# WRONG
if not request.user.profile.is_staff_or_admin():
    return redirect('home')
```
**Fix:** Use `@staff_required` decorator

### ❌ Duplicated Card HTML
```django
<!-- WRONG -->
<div class="card">
    <div class="card-header">...</div>
    <div class="card-body">...</div>
</div>
```
**Fix:** `{% include 'components/card.html' %}`

---

**Last Updated:** 2025-11-23
**Skills Version:** 2.0.0
**Always refer to:** `.claude/skills/README.md` for complete documentation

**Foundation components are mandatory - no exceptions!**
