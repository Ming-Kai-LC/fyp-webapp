# Deprecated Skills

**Date Deprecated:** 2025-11-23
**Reason:** Consolidation to reduce duplication and improve maintainability

---

## Skills Moved Here

These skills have been merged into other skills to create a more streamlined and maintainable skill system.

### 1. component-reusability → foundation-components
**Merged into:** `foundation-components/skill.md`
**Reason:** Foundation components is the concrete implementation of component reusability principles

**What was merged:**
- View mixins patterns
- Template component patterns
- Additional template tag examples (active_nav, query_transform)
- Component reusability checklist

**Use instead:** `foundation-components`

---

### 2. ui-ux-consistency → ui-design-system
**Merged into:** `ui-design-system/skill.md`
**Reason:** UI/UX consistency is part of the comprehensive design system

**What was merged:**
- Color palette
- Typography scale
- Spacing system
- Component patterns (cards, buttons, forms, tables, badges, alerts)
- Icon system mapping
- Accessibility guidelines

**Use instead:** `ui-design-system`

---

### 3. mobile-responsive → ui-design-system
**Merged into:** `ui-design-system/skill.md`
**Reason:** Responsive design is a core part of UI/UX design system

**What was merged:**
- Mobile-first approach
- Bootstrap 5 responsive breakpoints
- Responsive grid patterns
- Touch-friendly UI guidelines
- Responsive images, tables, navigation
- Testing checklist

**Use instead:** `ui-design-system`

---

### 4. django-module-creation → full-stack-django-patterns
**Merged into:** `full-stack-django-patterns/skill.md`
**Reason:** Full-stack Django patterns is a superset that includes all Django module creation best practices

**What was merged:**
- Fat Models, Thin Views pattern
- Class-Based Views (CBVs) with mixins
- Type hints and documentation standards
- Django app structure
- Model managers and querysets
- OOP principles for Django

**Use instead:** `full-stack-django-patterns`

---

## Impact of Consolidation

**Before:** 16 skills
**After:** 13 skills
**Reduction:** 3 skills (19% fewer)

**Benefits:**
- ✅ Less cognitive overhead (fewer skills to remember)
- ✅ No duplication (single source of truth)
- ✅ Better organization (related concepts grouped)
- ✅ Easier maintenance (update one skill instead of multiple)
- ✅ Clearer hierarchy (Foundation → Architecture → Best Practices)

---

## Migration Guide

If you were using any of these deprecated skills, update your references:

| Old Skill | New Skill | Location |
|-----------|-----------|----------|
| component-reusability | foundation-components | `.claude/skills/foundation-components/skill.md` |
| ui-ux-consistency | ui-design-system | `.claude/skills/ui-design-system/skill.md` |
| mobile-responsive | ui-design-system | `.claude/skills/ui-design-system/skill.md` |
| django-module-creation | full-stack-django-patterns | `.claude/skills/full-stack-django-patterns/skill.md` |

---

## Why Keep These Files?

These files are preserved in `_deprecated/` for:
1. **Historical reference** - See how the skills evolved
2. **Content verification** - Ensure all content was properly merged
3. **Rollback capability** - Can restore if needed (unlikely)

**Note:** These skills will NOT be loaded by Claude Code. Only active skills in `.claude/skills/` are loaded.

---

**Last Updated:** 2025-11-23
**Consolidated By:** Skills Refactoring Process
**Documentation:** See `.claude/SKILLS_CONSOLIDATION_SUMMARY.md`
