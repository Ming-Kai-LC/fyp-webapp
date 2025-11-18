# Claude Code Skills for COVID-19 Detection Webapp

This directory contains auto-applying skills that ensure consistency, quality, and best practices across all development sessions.

## 📁 Skill Structure (Proper Format)

Each skill is organized in its own folder with a `SKILL.md` file containing YAML frontmatter:

```
.claude/skills/
├── mobile-responsive/
│   └── SKILL.md                    # Mobile-first responsive design
├── ui-ux-consistency/
│   └── SKILL.md                    # Design system enforcement
├── django-module-creation/
│   └── SKILL.md                    # Django OOP best practices
├── security-best-practices/
│   └── SKILL.md                    # OWASP Top 10 + Healthcare security
├── performance-optimization/
│   └── SKILL.md                    # Database + RTX 4060 optimization
├── code-quality-standards/
│   └── SKILL.md                    # PEP 8 + Testing standards
├── component-reusability/
│   └── SKILL.md                    # DRY principles + Reusable components
└── standard-folder-structure/
    └── SKILL.md                    # Folder organization enforcement
```

## 📚 Available Skills

### 1. **Mobile-Responsive Design** 📱
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

### 2. **UI/UX Consistency** 🎨
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

### 3. **Django Module Creation** 🏗️
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

### 4. **Security Best Practices** 🔒
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

### 5. **Performance Optimization** ⚡
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

### 6. **Code Quality Standards** ✅
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

### 7. **Component Reusability** ♻️
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

### 8. **Standard Folder Structure** 📂
**Auto-applies to:** Creating modules, organizing files

Enforces consistent folder organization across all modules.

**Key Features:**
- Standard Django module structure
- File naming conventions
- Template organization (components/ vs pages/)
- Test structure mirroring
- Package structure guidelines
- Maximum file size limits (500 lines)

**When to use:** Creating new modules, organizing code, refactoring

---

## 🎯 How Skills Work Together

### Example: Creating a New Feature

When you ask Claude to create a new "Prediction Export" feature, these skills automatically apply:

1. **standard-folder-structure** → Creates correct directory structure
2. **django-module-creation** → Creates service layer, views with mixins
3. **security-best-practices** → Validates permissions, sanitizes data
4. **performance-optimization** → Optimizes queries, adds caching
5. **ui-ux-consistency** → Uses consistent UI patterns
6. **mobile-responsive** → Ensures mobile compatibility
7. **code-quality-standards** → Adds tests, type hints, documentation
8. **component-reusability** → Reuses existing components

---

## 📖 Using Skills

### Automatic Application

Claude Code automatically applies relevant skills based on the task. You don't need to explicitly invoke them.

**Example:**
```
You: "Create a patient dashboard page"

Claude will automatically apply:
- standard-folder-structure (organize templates correctly)
- mobile-responsive (make it responsive)
- ui-ux-consistency (use design system)
- django-module-creation (class-based view with mixins)
- security-best-practices (role-based access)
- performance-optimization (optimize queries)
- component-reusability (reuse existing components)
```

### How It Works Internally

1. **At Startup**: Claude Code pre-loads the `name` and `description` from each SKILL.md
2. **During Development**: Based on the task, relevant skills are automatically loaded
3. **Full Context**: Complete skill content is loaded only when needed (keeps context efficient)

---

## 📝 Skill File Format

Each SKILL.md follows this standard format:

```markdown
---
name: Skill Name
description: Brief description of what skill does and when it auto-applies
---

# Skill Content

## Core Principles
...

## Guidelines
...

## Examples
...

## Checklist
...

## Auto-Apply This Skill When:
- Trigger condition 1
- Trigger condition 2
...
```

The YAML frontmatter is critical - it tells Claude Code:
- **name**: What the skill is called
- **description**: When to auto-apply it

---

## 🏥 Healthcare-Specific Considerations

These skills include medical/healthcare specific patterns:

- **Patient data handling** (security-best-practices)
- **Medical terminology** (ui-ux-consistency)
- **Diagnosis display patterns** (component-reusability)
- **Audit logging** (security-best-practices)
- **Data retention** (security-best-practices)

---

## 🔄 Working Across Multiple Sessions

These skills enable consistent development across multiple sessions:

### At Session Start:
1. Skills auto-load, providing full context
2. Claude knows current project patterns and standards
3. No ramp-up time needed

### During Development:
1. Skills auto-apply based on task type
2. Consistent patterns enforced
3. Quality maintained automatically

### At Session End:
1. Confidence that code follows all standards
2. Ready for handoff to next session
3. Combined with session handoff docs for continuity

**Works seamlessly with:**
- `docs/MODULE_DEVELOPMENT_GUIDE.md` - How to create modules
- `docs/PROJECT_STRUCTURE.md` - Current project state
- `docs/SESSION_HANDOFF_TEMPLATE.md` - Session continuity
- `docs/VALIDATION_CHECKLIST.md` - Pre-commit validation
- `docs/TRACKING.md` - Progress tracking

---

## 📊 Skill Coverage

### Frontend (Templates/UI)
- ✅ mobile-responsive
- ✅ ui-ux-consistency
- ✅ component-reusability
- ✅ standard-folder-structure

### Backend (Django/Python)
- ✅ django-module-creation
- ✅ security-best-practices
- ✅ performance-optimization
- ✅ code-quality-standards
- ✅ standard-folder-structure

### ML/AI
- ✅ performance-optimization (VRAM management)
- ✅ security-best-practices (model validation)

---

## 🎓 Skills for Your FYP Thesis

When documenting your system in the thesis, these skills provide:

### Chapter 3 (Methodology)
- **django-module-creation** → System architecture patterns
- **security-best-practices** → Security measures implemented
- **performance-optimization** → Performance optimization strategies
- **standard-folder-structure** → Project organization

### Chapter 4 (Implementation)
- **ui-ux-consistency** → Design system documentation
- **mobile-responsive** → Responsive design approach
- **component-reusability** → Reusable component architecture

### Chapter 5 (Testing)
- **code-quality-standards** → Testing strategy and coverage

---

## ✅ Quality Assurance

Every skill includes checklists to ensure:
- ✅ Mobile responsiveness
- ✅ Security compliance
- ✅ Performance targets
- ✅ Code quality standards
- ✅ Accessibility requirements
- ✅ Folder structure consistency

---

## 🎯 Success Metrics

With these skills applied, your webapp achieves:

- **100% mobile responsive** pages
- **Consistent UI/UX** across all features
- **OWASP Top 10** security compliance
- **< 10 seconds** prediction time (all 6 models)
- **80%+** test coverage
- **Reusable components** throughout
- **Clean folder structure** everywhere
- **Production-ready** code quality

---

## 🚀 Getting Started

Just start coding! Claude will automatically apply relevant skills:

```bash
# Create a new feature
You: "Add a feature to export predictions to CSV"

# Claude applies:
# ✅ Standard Structure: Creates proper file organization
# ✅ Security: Validates permissions
# ✅ Performance: Optimizes query for export
# ✅ Code Quality: Adds tests and documentation
# ✅ Django: Uses service layer pattern
```

---

## 🔧 Customizing Skills

### Modifying Existing Skills
1. Navigate to the skill folder (e.g., `.claude/skills/mobile-responsive/`)
2. Edit `SKILL.md`
3. Keep under 500 lines for optimal performance
4. Maintain YAML frontmatter format
5. Update description if trigger conditions change

### Adding New Skills
1. Create folder: `.claude/skills/new-skill/`
2. Create `SKILL.md` with YAML frontmatter:
   ```markdown
   ---
   name: New Skill
   description: What it does and when it auto-applies
   ---

   # Content...
   ```
3. Document when it should auto-apply
4. Update this README
5. Test that it loads properly

---

## 📞 Support

If you notice:
- Missing patterns
- Inconsistencies
- Better approaches
- New best practices

Update the relevant skill file to capture the improvement!

---

**Last Updated**: 2025-11-18
**Total Skills**: 8
**Format**: Folder structure with SKILL.md + YAML frontmatter
**Total Content**: ~5,000 lines of best practices and patterns

**Your Django webapp now has a comprehensive, properly-formatted skill system that ensures professional-grade code automatically!** 🎉
