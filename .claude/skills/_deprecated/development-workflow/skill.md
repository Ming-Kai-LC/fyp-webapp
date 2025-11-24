# Development Workflow & Git Standards

**Version:** 1.0.0
**Last Updated:** 2025-11-22
**Auto-apply:** YES - Automatically enforces git standards during commits and PRs

---

## Purpose

This skill enforces consistent development workflow, git practices, commit standards, and code review processes. It ensures all code changes follow best practices and maintains high quality standards throughout the development lifecycle.

---

## When This Skill Auto-Triggers

Claude Code should **automatically apply this skill** when:
- User asks to create a git commit
- User requests to create a pull request
- User asks to create or switch branches
- User mentions "commit", "push", "PR", "pull request"
- Before running git commands via Bash tool
- During code review scenarios

**Examples:**
- "Commit these changes"
- "Create a PR for this feature"
- "Push to main branch"
- "Create a new branch for appointments"

---

## Git Workflow Overview

This project follows a **Git Flow** inspired workflow:

```
main (production-ready)
  ↑
  └─ develop (integration branch)
       ↑
       ├─ feature/feature-name
       ├─ bugfix/issue-number-description
       ├─ hotfix/critical-fix
       └─ release/v1.0.0
```

### Branch Types

1. **main** - Production-ready code, protected
2. **develop** - Integration branch for features (optional)
3. **feature/** - New features or enhancements
4. **bugfix/** - Bug fixes
5. **hotfix/** - Critical production fixes
6. **release/** - Release preparation

---

## Branch Naming Standards

### Format Rules

**Feature branches:**
```
feature/<short-description>
feature/<issue-number>-<short-description>
```

**Examples:**
```
feature/appointment-scheduling
feature/123-patient-dashboard
feature/ml-model-caching
```

**Bugfix branches:**
```
bugfix/<issue-number>-<short-description>
bugfix/<short-description>
```

**Examples:**
```
bugfix/456-fix-login-redirect
bugfix/permission-check-error
```

**Hotfix branches:**
```
hotfix/<critical-issue-description>
```

**Examples:**
```
hotfix/security-vulnerability
hotfix/data-leak-patient-records
```

**Release branches:**
```
release/v<major>.<minor>.<patch>
```

**Examples:**
```
release/v1.0.0
release/v1.2.0
```

### Naming Conventions

- Use lowercase
- Use hyphens (-) not underscores (_)
- Be descriptive but concise (3-5 words max)
- Include issue number when applicable
- No special characters except hyphens

**Good:**
```
feature/notification-system
bugfix/123-xray-upload-validation
hotfix/csrf-token-expiry
```

**Bad:**
```
feature/New_Feature_123  ❌ (underscores, caps)
bugfix/fix               ❌ (not descriptive)
my-branch                ❌ (no type prefix)
feature/this-is-a-very-long-branch-name-that-describes-everything  ❌ (too long)
```

### Creating Branches

**Claude Code should auto-create branches with correct naming:**

```bash
# For new feature
git checkout -b feature/appointment-scheduling

# For bug fix
git checkout -b bugfix/789-form-validation

# For hotfix
git checkout -b hotfix/security-patch
```

---

## Commit Message Standards

### Conventional Commits Format

**All commits MUST follow Conventional Commits specification:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(api): Add batch prediction endpoint` |
| `fix` | Bug fix | `fix(auth): Correct permission check for staff` |
| `docs` | Documentation only | `docs(readme): Update installation instructions` |
| `style` | Code style (formatting, no logic change) | `style(forms): Format with black` |
| `refactor` | Code refactoring (no feature/fix) | `refactor(services): Extract common logic` |
| `perf` | Performance improvement | `perf(queries): Add select_related for patients` |
| `test` | Adding/updating tests | `test(appointments): Add permission tests` |
| `chore` | Build/tooling changes | `chore(deps): Update Django to 5.1.1` |
| `ci` | CI/CD changes | `ci(github): Add coverage reporting` |
| `security` | Security fixes | `security(api): Fix JWT token expiration` |

### Scope

Optional but recommended. Indicates module/component affected:

- `api` - API endpoints
- `auth` - Authentication/authorization
- `detection` - COVID detection module
- `appointments` - Appointments module
- `dashboards` - Dashboards
- `models` - Database models
- `forms` - Forms
- `tests` - Tests
- `deps` - Dependencies

### Subject

- First line, max 72 characters
- Imperative mood ("Add feature" not "Added feature")
- No period at end
- Capitalize first letter
- Clear and concise

**Good:**
```
feat(appointments): Add appointment cancellation feature
fix(auth): Correct staff permission check in dashboard
docs(api): Update API documentation for v1 endpoints
```

**Bad:**
```
Added new feature  ❌ (no type, past tense)
fix.  ❌ (not descriptive, has period)
FEAT: NEW STUFF  ❌ (all caps, vague)
```

### Body

- Optional, but recommended for complex changes
- Explain **why** not **what** (code shows what)
- Separate from subject with blank line
- Wrap at 72 characters
- Multiple paragraphs OK

### Footer

- Optional
- Reference issues: `Closes #123`, `Fixes #456`, `Refs #789`
- Breaking changes: `BREAKING CHANGE: Description`
- Co-authors: `Co-Authored-By: Name <email>`

### Complete Example

```
feat(appointments): Add appointment scheduling system

Implement complete appointment scheduling with:
- Staff can create/update/cancel appointments
- Patients can view their own appointments
- Email notifications on creation and reminders
- Conflict detection for time slots
- Business hours validation (9 AM - 5 PM)

This resolves the patient scheduling workflow requirement
and provides foundation for future calendar integration.

Closes #123
Refs #456
```

### Quick Commit Examples

**Feature:**
```
feat(notifications): Add email notification system

Implement email notifications for:
- Appointment confirmations
- Appointment reminders (24 hours before)
- Prediction results ready

Uses Django email backend with templates.

Closes #234
```

**Bug Fix:**
```
fix(auth): Correct permission check for patient data access

Patients were able to see other patients' X-ray results
due to missing object-level permission check in the
XRayDetailView. Added IsPatientOwner permission class.

Fixes #567
Security: CVE-2024-XXXX
```

**Refactor:**
```
refactor(services): Extract prediction logic to service layer

Move prediction workflow from views to PredictionService:
- Better separation of concerns
- Reusable across web, API, and CLI
- Easier to test in isolation

Refs #890
```

**Tests:**
```
test(appointments): Add comprehensive test suite

Add tests for:
- Model validation and methods
- Form validation (business hours, conflicts)
- Permission enforcement (admin/staff/patient)
- API endpoints for all roles
- E2E appointment workflow

Coverage: 87%
```

**Documentation:**
```
docs(api): Update API documentation with examples

Add request/response examples for all endpoints:
- Authentication (login, refresh, logout)
- Predictions (create, retrieve, list)
- Appointments (CRUD operations)

Includes curl examples and error responses.
```

---

## Creating Commits (Auto-Process)

**When user asks to commit, Claude Code should:**

### Step 1: Check Status

```bash
git status
```

Review:
- Modified files
- Untracked files
- Staged files

### Step 2: Analyze Changes

```bash
git diff
git diff --staged  # If files already staged
```

Understand:
- What changed?
- Why changed?
- What type of commit? (feat, fix, refactor, etc.)
- What scope? (module/component)

### Step 3: Stage Relevant Files

```bash
# Stage specific files
git add <file1> <file2>

# Or stage all (if appropriate)
git add .
```

**NEVER stage:**
- `.env` files (secrets!)
- `credentials.json` or similar
- `*.pyc`, `__pycache__/`
- `db.sqlite3` (unless explicitly requested)
- IDE files (`.vscode/`, `.idea/`)
- Large binary files without confirmation

### Step 4: Draft Commit Message

Based on changes, draft a Conventional Commit message:

```python
# Analyze changes
type = "feat"  # or fix, docs, etc.
scope = "appointments"  # module affected
subject = "Add appointment cancellation feature"

body = """
Allow staff to cancel appointments with reason tracking:
- Add cancellation_reason field to Appointment model
- Create cancel view with staff-only permission
- Send cancellation email to patient
- Update appointment status to CANCELLED

Staff can provide optional reason for audit purposes.
"""

footer = "Closes #123"

# Construct message
message = f"{type}({scope}): {subject}\n\n{body}\n\n{footer}"
```

### Step 5: Create Commit

**Use HEREDOC for proper formatting:**

```bash
git commit -m "$(cat <<'EOF'
feat(appointments): Add appointment cancellation feature

Allow staff to cancel appointments with reason tracking:
- Add cancellation_reason field to Appointment model
- Create cancel view with staff-only permission
- Send cancellation email to patient
- Update appointment status to CANCELLED

Staff can provide optional reason for audit purposes.

Closes #123
EOF
)"
```

### Step 6: Verify Commit

```bash
git log -1 --format=fuller
```

Check:
- Commit message formatted correctly
- Author information correct
- Files included as expected

### Example: Complete Commit Flow

**User:** "Commit these changes"

**Claude Code auto-response:**

```bash
# 1. Check status
git status

# Output shows:
# modified: appointments/models.py
# modified: appointments/views.py
# new file: appointments/tests/test_views.py

# 2. Review changes
git diff

# Sees: Added cancellation feature

# 3. Stage files
git add appointments/models.py appointments/views.py appointments/tests/test_views.py

# 4. Create commit
git commit -m "$(cat <<'EOF'
feat(appointments): Add appointment cancellation feature

Allow staff to cancel appointments with reason tracking:
- Add cancellation_reason field to Appointment model
- Create cancel view with staff-only permission
- Send cancellation email to patient
- Update appointment status to CANCELLED

Staff can provide optional reason for audit purposes.

Includes comprehensive tests for cancellation workflow.

Closes #123
EOF
)"

# 5. Verify
git log -1
```

---

## Pull Request Standards

### When to Create PR

**Create PR when:**
- Feature complete and tested
- All tests pass locally
- Code reviewed by yourself
- Documentation updated
- Ready for team review

**DO NOT create PR when:**
- Work in progress (use draft PR instead)
- Tests failing
- Incomplete feature
- Experimental/spike work

### PR Template

Create `.github/pull_request_template.md`:

```markdown
## Summary

<!-- Brief description of what this PR does (2-3 sentences) -->

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Security fix

## Related Issue(s)

<!-- Link to related issues -->

Closes #
Refs #

## Changes Made

<!-- Detailed list of changes -->

-
-
-

## Testing Done

<!-- Describe testing performed -->

### Unit Tests
- [ ] All new code has unit tests
- [ ] All tests pass locally
- [ ] Coverage ≥ 80%

### Integration Tests
- [ ] Integration tests added/updated
- [ ] Tests pass locally

### Manual Testing
- [ ] Tested in browser (if UI changes)
- [ ] Tested with different user roles (admin/staff/patient)
- [ ] Tested edge cases
- [ ] Tested error scenarios

### Test Evidence
<!-- Screenshots, test output, coverage report -->

```
Coverage Report:
- appointments/models.py: 92%
- appointments/views.py: 85%
- appointments/services.py: 88%
Overall: 87%
```

## Database Changes

<!-- If applicable -->

- [ ] Migration created
- [ ] Migration tested locally
- [ ] Migration is reversible
- [ ] Data migration included (if needed)
- [ ] Migration tested on production-like data

## Security Considerations

<!-- Security implications -->

- [ ] Input validation added
- [ ] Permission checks implemented
- [ ] No sensitive data exposed
- [ ] OWASP Top 10 reviewed
- [ ] Security scan passed (bandit)

## Performance Impact

<!-- Performance considerations -->

- [ ] No N+1 queries introduced
- [ ] Appropriate indexes added
- [ ] Query optimization considered
- [ ] Caching strategy considered

## Documentation

- [ ] Code comments added (where needed)
- [ ] Docstrings updated
- [ ] README.md updated (if needed)
- [ ] API documentation updated (if applicable)
- [ ] CHANGELOG.md updated

## Checklist

<!-- Verify all items before requesting review -->

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Coverage ≥ 80%
- [ ] No console warnings or errors
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits
- [ ] Branch up to date with base branch
- [ ] GitHub Actions CI passing
- [ ] No merge conflicts

## Screenshots (if applicable)

<!-- Add screenshots for UI changes -->

## Additional Notes

<!-- Any additional information for reviewers -->

---

**Reviewer Checklist:**

- [ ] Code quality acceptable
- [ ] Tests comprehensive
- [ ] Security reviewed
- [ ] Performance acceptable
- [ ] Documentation clear
- [ ] Approved for merge
```

### Creating PR (Auto-Process)

**When user asks to create PR, Claude Code should:**

#### Step 1: Verify Branch Status

```bash
# Check current branch
git branch --show-current

# Check if up to date with remote
git fetch origin
git status

# Check if commits pushed
git log origin/$(git branch --show-current)..HEAD
```

#### Step 2: Run Tests Locally

```bash
# Run full test suite
venv/Scripts/python.exe -m pytest --cov=. --cov-report=term-missing

# Verify coverage ≥ 80%
# Verify all tests pass
```

#### Step 3: Push Branch

```bash
# If not pushed yet
git push -u origin <branch-name>

# If already exists
git push origin <branch-name>
```

#### Step 4: Analyze Changes for PR Description

```bash
# Get all commits in this branch
git log main..HEAD --oneline

# Get full diff from main
git diff main...HEAD
```

#### Step 5: Generate PR Summary

Based on all commits and changes:

```markdown
## Summary

This PR implements a comprehensive appointment scheduling system for the COVID-19 Detection webapp. Staff can create, update, and cancel appointments. Patients can view their own appointments. The system includes conflict detection, business hours validation, and email notifications.

## Type of Change

- [x] New feature
- [x] Documentation update

## Related Issue(s)

Closes #123
Closes #124
Refs #125

## Changes Made

- Added `Appointment` model with status tracking and business logic
- Created `AppointmentService` for appointment workflow orchestration
- Implemented staff-only views for CRUD operations
- Added patient view for listing own appointments
- Integrated email notifications (confirmation, reminders, cancellations)
- Created comprehensive test suite (87% coverage)
- Added API endpoints for appointments with role-based permissions
- Updated documentation with appointment module guide

## Testing Done

### Unit Tests
- [x] All new code has unit tests
- [x] All tests pass locally
- [x] Coverage 87% (above 80% threshold)

### Manual Testing
- [x] Tested appointment creation as staff
- [x] Tested patient viewing own appointments
- [x] Tested permission enforcement (patients cannot create)
- [x] Tested conflict detection
- [x] Tested business hours validation
- [x] Tested email notifications

### Test Evidence

```
pytest output:
========================= test session starts =========================
collected 47 items

appointments/tests/test_models.py::TestAppointmentModel PASSED [100%]
appointments/tests/test_views.py::TestAppointmentListView PASSED [100%]
...

Coverage: 87%
All tests passed ✅
```

## Database Changes

- [x] Migration created: `0001_initial.py`
- [x] Migration tested locally
- [x] Migration is reversible
- [x] No data migration needed (new module)

## Security Considerations

- [x] Form validation for all user inputs
- [x] Permission checks: Staff-only for create/update/delete
- [x] Object-level permissions: Patients see own appointments only
- [x] CSRF protection enabled
- [x] No sensitive data in logs

## Documentation

- [x] Docstrings on all classes and methods
- [x] README.md updated with appointment module
- [x] API documentation updated

## Screenshots

[Attachment: appointment-list.png]
[Attachment: appointment-create.png]
```

#### Step 6: Create PR Using gh CLI

```bash
gh pr create \
  --title "feat(appointments): Add appointment scheduling system" \
  --body "$(cat <<'EOF'
## Summary

This PR implements a comprehensive appointment scheduling system...
[Full PR description from above]
EOF
)" \
  --base main \
  --head feature/appointment-scheduling
```

**OR provide user with URL:**
```
Visit: https://github.com/Ming-Kai-LC/fyp-webapp/compare/main...feature/appointment-scheduling
```

---

## Code Review Guidelines

### For Authors (Self-Review)

**Before requesting review, check:**

- [ ] Code is clean and readable
- [ ] No commented-out code (remove it)
- [ ] No console.log or print() statements (except logging)
- [ ] No TODO comments without issue numbers
- [ ] Variable names are descriptive
- [ ] Functions are small and focused (<50 lines)
- [ ] No duplicate code (DRY principle)
- [ ] Error handling implemented
- [ ] Edge cases handled
- [ ] Tests added for new code
- [ ] Documentation updated

### For Reviewers

**Review checklist:**

#### 1. Correctness
- [ ] Code does what PR description says
- [ ] Logic is correct
- [ ] Edge cases handled
- [ ] Error scenarios handled

#### 2. Security
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Permission checks implemented
- [ ] Secrets not hardcoded
- [ ] OWASP Top 10 considered

#### 3. Performance
- [ ] No N+1 queries
- [ ] Appropriate database indexes
- [ ] Efficient algorithms used
- [ ] No unnecessary computations in loops
- [ ] Caching used where appropriate

#### 4. Tests
- [ ] Tests added for new code
- [ ] Tests cover edge cases
- [ ] Tests are readable
- [ ] Mocking used appropriately
- [ ] Coverage ≥ 80%

#### 5. Code Quality
- [ ] Follows project style guide
- [ ] PEP 8 compliant
- [ ] Type hints present
- [ ] Docstrings present
- [ ] Code is DRY
- [ ] Appropriate abstractions

#### 6. Documentation
- [ ] README updated if needed
- [ ] API docs updated
- [ ] Inline comments where needed
- [ ] Commit messages clear

### Review Comments Guidelines

**Good review comments:**

```
✅ "Consider adding an index on the scheduled_date field since we're
   filtering by it frequently. This could improve query performance."

✅ "This validation logic is duplicated in forms.py:45. Could we extract
   it to a utility function?"

✅ "Great job on the test coverage! Could we also add a test for the
   edge case where scheduled_date is exactly at 9 AM?"
```

**Bad review comments:**

```
❌ "This is wrong." (not specific)

❌ "Why did you do it this way?" (sounds accusatory)

❌ "I wouldn't have done it like this." (not constructive)
```

**Tone guidelines:**
- Be respectful and constructive
- Ask questions rather than demand changes
- Provide reasoning for suggestions
- Praise good solutions
- Assume good intentions

---

## Git Workflow Integration

### Common Git Commands (Auto-Apply Standards)

**Creating Feature Branch:**
```bash
# Claude Code auto-generates proper name
git checkout -b feature/notification-system
```

**Committing Changes:**
```bash
# Claude Code auto-generates Conventional Commit message
git add <files>
git commit -m "$(cat <<'EOF'
feat(notifications): Add email notification system
...
EOF
)"
```

**Creating PR:**
```bash
# Claude Code auto-generates PR description
gh pr create --title "..." --body "..."
```

**Merging PR:**
```bash
# After approval, merge with squash (recommended)
gh pr merge <pr-number> --squash --delete-branch
```

---

## Integration with TodoWrite Tool

**Automatically create git workflow todos:**

```
Before committing:
- [ ] Review all changed files
- [ ] Ensure no sensitive data in code
- [ ] Run pre-commit hooks
- [ ] Verify tests pass
- [ ] Draft commit message (Conventional Commits)
- [ ] Stage relevant files
- [ ] Create commit
- [ ] Verify commit message formatted correctly

Before creating PR:
- [ ] Ensure branch up to date with main
- [ ] Run full test suite locally
- [ ] Verify coverage ≥ 80%
- [ ] Push branch to remote
- [ ] Review all commits in branch
- [ ] Generate PR summary and description
- [ ] Create PR using gh CLI or web
- [ ] Add reviewers
- [ ] Link related issues

After PR created:
- [ ] Monitor CI/CD status
- [ ] Address review comments
- [ ] Update PR based on feedback
- [ ] Get approval from reviewers
- [ ] Merge PR
- [ ] Delete feature branch
```

---

## Commit Message Templates

### Feature Commit

```
feat(<scope>): <short description>

<Why this feature is needed>
<What it does>
<How it works (if complex)>

Key changes:
- <change 1>
- <change 2>
- <change 3>

Closes #<issue>
```

### Bug Fix Commit

```
fix(<scope>): <short description of fix>

<What was broken>
<Why it was broken>
<How the fix works>

Root cause: <explanation>
Solution: <explanation>

Fixes #<issue>
```

### Refactor Commit

```
refactor(<scope>): <short description>

<Why refactoring was needed>
<What was refactored>
<Benefits of refactor>

Changes:
- <change 1>
- <change 2>

No functional changes.

Refs #<issue>
```

### Test Commit

```
test(<scope>): <short description>

Add tests for:
- <test type 1>
- <test type 2>
- <test type 3>

Coverage before: X%
Coverage after: Y%

Refs #<issue>
```

---

## Success Criteria

Development workflow is complete when:

✅ All branches follow naming conventions
✅ All commits follow Conventional Commits format
✅ PR template configured and used
✅ All PRs have comprehensive descriptions
✅ Code review checklist followed
✅ Pre-commit hooks enforcing standards
✅ GitHub Actions enforcing quality gates
✅ Branch protection rules active
✅ Team following workflow consistently

---

## Common Pitfalls to Avoid

1. **❌ Vague commit messages** - "fix stuff", "update code"
2. **❌ Not using type prefix** - Missing feat/fix/docs, etc.
3. **❌ Committing sensitive data** - .env files, API keys
4. **❌ Large commits** - Commit frequently, keep commits focused
5. **❌ Missing issue references** - Always link to issues
6. **❌ Skipping PR description** - Poor descriptions slow reviews
7. **❌ Not testing before PR** - Always run tests locally first
8. **❌ Force pushing to main** - NEVER force push to protected branches
9. **❌ Merge conflicts** - Keep branch up to date with main
10. **❌ Rushing reviews** - Take time to review thoroughly

---

## Integration with Existing Skills

This skill **automatically integrates** with:

1. **`module-creation-lifecycle`** - Creates commits during module development
2. **`testing-automation`** - Verifies tests pass before commits/PRs
3. **`user-role-permissions`** - Mentions permissions in commit messages
4. **`security-best-practices`** - Flags security issues in code review
5. **`code-quality-standards`** - Enforces PEP 8 in pre-commit hooks

---

## Version History

- **1.0.0** (2025-11-22): Initial version with full git workflow standards

---

**Last Updated:** 2025-11-22
