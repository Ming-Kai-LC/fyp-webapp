# Claude Code Skills for COVID-19 Detection Webapp

This directory contains specialized skills that Claude Code will automatically apply when developing the COVID-19 Detection web application. These skills ensure consistency, quality, and best practices across all development work.

## 📚 Available Skills

### 1. **mobile-responsive.md** 📱
**Auto-applies to:** All UI/template work

Ensures all interfaces are mobile-first and responsive across all devices.

**Key Features:**
- Mobile-first design approach
- Bootstrap 5 responsive grid system
- Touch-friendly UI (44x44px minimum targets)
- Responsive images, tables, and navigation
- Breakpoint testing guidelines

**When to use:** Creating/modifying any template or UI component

---

### 2. **ui-ux-consistency.md** 🎨
**Auto-applies to:** All UI work, component creation

Maintains consistent design language throughout the application.

**Key Features:**
- Consistent color palette and typography
- Standard component patterns (cards, buttons, forms)
- Bootstrap Icons mapping
- Medical/healthcare specific patterns
- Accessibility standards (WCAG 2.1)

**When to use:** Creating new pages, components, or modifying existing UI

---

### 3. **django-module-creation.md** 🏗️
**Auto-applies to:** Creating new features, models, views

Ensures Django code follows industry best practices using OOP principles.

**Key Features:**
- Fat models, thin views pattern
- Class-based views with mixins
- Service layer for business logic
- Custom managers and querysets
- Type hints and comprehensive documentation
- Reusable template tags

**When to use:** Adding new models, views, forms, or business logic

---

### 4. **security-best-practices.md** 🔒
**Auto-applies to:** All code, especially auth and data handling

Enforces security best practices for healthcare applications.

**Key Features:**
- OWASP Top 10 protection
- Input validation and sanitization
- CSRF/XSS prevention
- Secure file upload handling
- HIPAA-like considerations
- Audit logging
- Data encryption guidelines

**When to use:** Handling user input, authentication, sensitive data, file uploads

---

### 5. **performance-optimization.md** ⚡
**Auto-applies to:** Database queries, ML inference, caching

Ensures optimal performance, especially for RTX 4060 8GB GPU.

**Key Features:**
- N+1 query prevention
- Database indexing strategy
- Caching patterns (view, fragment, low-level)
- ML inference optimization (VRAM management)
- Pagination best practices
- Static file optimization

**When to use:** Writing queries, ML inference, working with large datasets

---

### 6. **code-quality-standards.md** ✅
**Auto-applies to:** All code

Maintains high code quality and test coverage.

**Key Features:**
- PEP 8 compliance
- Type hints for all functions
- Comprehensive docstrings (Google style)
- Unit testing guidelines
- Test factories
- Code quality tools (Black, Flake8, pytest)

**When to use:** Writing any new code or refactoring

---

### 7. **component-reusability.md** ♻️
**Auto-applies to:** Creating components, templates, views

Maximizes code reuse through components and mixins.

**Key Features:**
- Reusable template components
- Custom template tags
- View mixins
- Abstract base models
- Form widgets
- Component library structure

**When to use:** Creating new features, noticing repeated code

---

## 🎯 How Skills Work Together

### Example: Creating a New Feature

When you ask Claude to create a new "Prediction Export" feature, these skills automatically apply:

1. **django-module-creation.md** → Creates service layer, views with mixins
2. **security-best-practices.md** → Validates permissions, sanitizes data
3. **performance-optimization.md** → Optimizes queries, adds caching
4. **ui-ux-consistency.md** → Uses consistent UI patterns
5. **mobile-responsive.md** → Ensures mobile compatibility
6. **code-quality-standards.md** → Adds tests, type hints, documentation
7. **component-reusability.md** → Reuses existing components

---

## 📖 Using Skills

### Automatic Application

Claude Code automatically applies relevant skills based on the task. You don't need to explicitly invoke them.

**Example:**
```
You: "Create a patient dashboard page"

Claude will automatically apply:
- mobile-responsive (make it responsive)
- ui-ux-consistency (use design system)
- django-module-creation (class-based view with mixins)
- security-best-practices (role-based access)
- performance-optimization (optimize queries)
- component-reusability (reuse existing components)
```

### Manual Reference

Reference a specific skill:
```
You: "Apply security-best-practices when handling file uploads"
```

---

## 🏥 Healthcare-Specific Considerations

These skills include medical/healthcare specific patterns:

- **Patient data handling** (security-best-practices)
- **Medical terminology** (ui-ux-consistency)
- **Diagnosis display patterns** (component-reusability)
- **Audit logging** (security-best-practices)
- **Data retention** (security-best-practices)

---

## 🎓 Skills for Your FYP Thesis

When documenting your system in the thesis, these skills provide:

### Chapter 3 (Methodology)
- **django-module-creation** → System architecture patterns
- **security-best-practices** → Security measures implemented
- **performance-optimization** → Performance optimization strategies

### Chapter 4 (Implementation)
- **ui-ux-consistency** → Design system documentation
- **mobile-responsive** → Responsive design approach
- **component-reusability** → Reusable component architecture

### Chapter 5 (Testing)
- **code-quality-standards** → Testing strategy and coverage

---

## 🔄 Skill Updates

Skills can be updated as the project evolves:

1. **Add new patterns** discovered during development
2. **Refine existing guidelines** based on experience
3. **Add project-specific conventions**

---

## ✅ Quality Assurance

Every skill includes checklists to ensure:
- Mobile responsiveness
- Security compliance
- Performance targets
- Code quality standards
- Accessibility requirements

---

## 📊 Skill Coverage

### Frontend (Templates/UI)
- ✅ mobile-responsive
- ✅ ui-ux-consistency
- ✅ component-reusability

### Backend (Django/Python)
- ✅ django-module-creation
- ✅ security-best-practices
- ✅ performance-optimization
- ✅ code-quality-standards

### ML/AI
- ✅ performance-optimization (VRAM management)
- ✅ security-best-practices (model validation)

---

## 🎯 Success Metrics

With these skills applied, your webapp achieves:

- **100% mobile responsive** pages
- **Consistent UI/UX** across all features
- **OWASP Top 10** security compliance
- **< 10 seconds** prediction time (all 6 models)
- **80%+** test coverage
- **Reusable components** throughout
- **Production-ready** code quality

---

## 🚀 Getting Started

Just start coding! Claude will automatically apply relevant skills:

```bash
# Create a new feature
You: "Add a feature to export predictions to CSV"

# Claude applies:
# ✅ Security: Validate permissions
# ✅ Performance: Optimize query for export
# ✅ Code Quality: Add tests and documentation
# ✅ Django: Use service layer pattern
```

---

## 📞 Support

If you notice:
- Missing patterns
- Inconsistencies
- Better approaches

Update the relevant skill file to capture the improvement!

---

**Your Django webapp now has a comprehensive skill system that ensures professional-grade code automatically!** 🎉
