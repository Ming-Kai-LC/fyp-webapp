# Announcements Module - Manual Testing Plan

**Server:** http://localhost:8000/
**Created:** 2025-11-23
**Module:** Announcements (Foundation Components Demo)

---

## Test Objectives

1. Verify all foundation components working in production
2. Test role-based access control (admin, staff, patient)
3. Validate UI/UX consistency and responsiveness
4. Confirm CRUD operations function correctly
5. Test template components, tags, and widgets

---

## Pre-Testing Checklist

- [x] Django migrations applied
- [x] Module added to INSTALLED_APPS
- [x] URLs configured in config/urls.py
- [x] Development server running
- [ ] Test users created (admin, staff, patient)
- [ ] Database has sample data

---

## Test User Requirements

You'll need the following users to test all permission scenarios:

### Admin User
- **Username:** admin
- **Role:** Admin (full privileges)
- **Can:** Create, read, update announcements

### Staff User
- **Username:** staff_user
- **Role:** Staff (read/update + limited create/delete)
- **Can:** Create, read, update announcements

### Patient User
- **Username:** patient_user
- **Role:** Patient (self-service only)
- **Can:** Read announcements only (no create/update)

**Create users via:** Django admin panel at http://localhost:8000/admin/

---

## Test Cases

### Test 1: Anonymous User Access Control
**Objective:** Verify unauthenticated users are redirected to login

**Steps:**
1. Open browser in incognito/private mode
2. Navigate to http://localhost:8000/announcements/
3. Verify redirect to login page
4. Try http://localhost:8000/announcements/create/
5. Verify redirect to login page

**Expected Result:**
- All announcement URLs redirect to `/accounts/login/`
- No access without authentication

**Foundation Components Tested:**
- `@login_required` decorator (views.py:16)
- `@staff_required` decorator (views.py:29)

---

### Test 2: Patient User - Read-Only Access
**Objective:** Verify patients can view but not create announcements

**Steps:**
1. Login as patient user
2. Navigate to http://localhost:8000/announcements/
3. Verify announcement list displays
4. Check that "Create Announcement" button is NOT visible
5. Manually navigate to http://localhost:8000/announcements/create/
6. Verify "Permission denied" message and redirect

**Expected Result:**
- Patient can view announcement list
- No create/update buttons visible
- Direct URL access blocked with error message

**Foundation Components Tested:**
- `@staff_required` decorator blocks patients (views.py:29)
- Template permission check: `{% if user.profile.is_staff_or_admin %}` (announcement_list.html:54)

---

### Test 3: Staff User - Create Announcement
**Objective:** Test announcement creation with Bootstrap widgets

**Steps:**
1. Login as staff user
2. Navigate to http://localhost:8000/announcements/
3. Click "Create Announcement" button
4. Fill in form:
   - **Title:** "COVID-19 Vaccination Drive"
   - **Message:** "Free vaccination available at clinic this week"
   - **Priority:** Warning
   - **Is Active:** Checked
   - **Expires At:** Set date 7 days in future
5. Submit form
6. Verify success message displayed
7. Verify redirect to announcement list
8. Verify new announcement appears in list

**Expected Result:**
- Form displays with Bootstrap 5 styling
- All fields use Bootstrap widgets (no hardcoded classes)
- DateTime picker works correctly
- Success message: "Announcement created successfully!"
- New announcement appears in list with warning badge

**Foundation Components Tested:**
- ✅ `BootstrapTextInput` widget (forms.py:109)
- ✅ `BootstrapTextarea` widget (forms.py:110)
- ✅ `BootstrapSelect` widget (forms.py:111)
- ✅ `BootstrapCheckboxInput` widget (forms.py:112)
- ✅ `BootstrapDateTimeInput` widget (forms.py:113)
- ✅ `{% status_badge %}` template tag (announcement_list.html:15)
- ✅ `{% format_datetime %}` template tag (announcement_list.html:34)
- ✅ Card component: `{% include 'components/card.html' %}` (announcement_list.html:11)

---

### Test 4: Admin User - Full CRUD Operations
**Objective:** Test complete announcement lifecycle

**Steps:**
1. Login as admin user
2. Navigate to http://localhost:8000/announcements/

**Create:**
3. Click "Create Announcement"
4. Create announcement with title "System Maintenance Notice"
5. Set priority to "Urgent"
6. Submit and verify creation

**Read:**
7. View announcement list
8. Click on announcement to view details
9. Verify all fields displayed correctly

**Update:**
10. Click "Edit" button on announcement detail page
11. Change priority from "Urgent" to "Info"
12. Update message text
13. Submit and verify update message
14. Verify changes reflected in list and detail views

**Expected Result:**
- All CRUD operations succeed
- Status badges change color based on priority
- Timestamps update correctly (created_at, updated_at from TimeStampedModel)
- UI remains consistent across all pages

**Foundation Components Tested:**
- ✅ `TimeStampedModel` base class (models.py:46)
- ✅ Auto `created_at` field (no manual definition needed)
- ✅ Auto `updated_at` field (updates on save)
- ✅ Bootstrap form widgets in update form
- ✅ All template tags and components

---

### Test 5: Template Components & Tags
**Objective:** Verify all foundation template components rendering correctly

**Steps:**
1. Login as any authenticated user
2. Navigate to announcement list
3. Inspect page elements

**Check Card Component:**
- Each announcement uses card component
- Proper Bootstrap structure (card, card-header, card-body)
- No duplicated HTML

**Check Status Badges:**
- Info priority → Blue badge
- Warning priority → Yellow badge
- Urgent priority → Red badge
- Badge styling consistent with UI_UX_DESIGN_SYSTEM.md

**Check Date Formatting:**
- All dates formatted consistently
- Format: "22 Nov 2025, 2:30 PM"
- Time zone: Asia/Kuala_Lumpur

**Check Pagination:**
- If >10 announcements, pagination appears
- Previous/Next buttons work
- Page numbers clickable
- Current page highlighted

**Expected Result:**
- All components render correctly
- Consistent styling across all elements
- No hardcoded HTML duplication
- Mobile responsive design

**Foundation Components Tested:**
- ✅ `{% include 'components/card.html' %}` (announcement_list.html:11)
- ✅ `{% include 'components/alert.html' %}` (for messages)
- ✅ `{% status_badge priority %}` (announcement_list.html:15)
- ✅ `{% format_datetime created_at %}` (announcement_list.html:34)
- ✅ `{% render_pagination page_obj %}` (announcement_list.html:52)

---

### Test 6: Form Validation
**Objective:** Test custom validation and error handling

**Steps:**
1. Login as staff/admin
2. Go to create announcement
3. Leave title blank and submit
4. Verify error message displayed
5. Enter title but leave message blank
6. Verify error message
7. Set expiration date in the past
8. Verify custom validation error: "Expiration date must be in the future"
9. Fill all fields correctly and submit
10. Verify success

**Expected Result:**
- Required field validation works
- Custom `clean_expires_at()` validation works (forms.py:119)
- Error messages displayed in Bootstrap alert style
- Form retains entered values on validation error

**Foundation Components Tested:**
- ✅ Form validation patterns (forms.py:119-124)
- ✅ Bootstrap error styling via widgets
- ✅ Alert component for error messages

---

### Test 7: Responsive Design
**Objective:** Test mobile-first responsive design

**Steps:**
1. Open announcement list in browser
2. Open browser DevTools (F12)
3. Toggle device toolbar (Ctrl+Shift+M)
4. Test at different breakpoints:
   - **Mobile (375px):** Card stacks vertically, buttons full-width
   - **Tablet (768px):** 2 columns, buttons inline
   - **Desktop (1200px):** 3 columns, full layout

**Expected Result:**
- Layout adapts to screen size
- Text remains readable
- Buttons accessible on touch devices
- No horizontal scrolling
- Follows Bootstrap 5 responsive grid

**Foundation Components Tested:**
- ✅ Mobile-responsive design (mobile-responsive skill)
- ✅ Bootstrap 5 grid system
- ✅ Responsive card components

---

### Test 8: Code Quality Verification
**Objective:** Verify DRY principles and code reduction

**Steps:**
1. Open browser DevTools
2. Inspect form elements
3. Verify Bootstrap classes applied automatically:
   - Text inputs have `form-control` class
   - Select dropdowns have `form-select` class
   - Checkboxes have `form-check-input` class
   - DateTime inputs have `form-control` and `type="datetime-local"`

4. View page source
5. Search for hardcoded Bootstrap classes
6. Verify NO instances of hardcoded `attrs={'class': 'form-control'}`

**Expected Result:**
- All Bootstrap classes applied via widgets
- Zero hardcoded widget attributes in templates
- Consistent styling across all forms
- DRY principles enforced

**Foundation Components Tested:**
- ✅ Bootstrap widget library (forms.py:97-102)
- ✅ Component reusability (component-reusability skill)
- ✅ Code quality standards (code-quality-standards skill)

---

## Test Results Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| Test 1: Anonymous Access | ⬜ Not Run | |
| Test 2: Patient Read-Only | ⬜ Not Run | |
| Test 3: Staff Create | ⬜ Not Run | |
| Test 4: Admin CRUD | ⬜ Not Run | |
| Test 5: Template Components | ⬜ Not Run | |
| Test 6: Form Validation | ⬜ Not Run | |
| Test 7: Responsive Design | ⬜ Not Run | |
| Test 8: Code Quality | ⬜ Not Run | |

**Overall Pass Rate:** 0/8 (0%)

---

## Foundation Components Verification

**Check each component is working:**

### 1. TimeStampedModel ⬜
- [ ] `created_at` auto-set on creation
- [ ] `updated_at` auto-updates on save
- [ ] No manual timestamp fields in models.py

### 2. Bootstrap Widgets ⬜
- [ ] BootstrapTextInput renders with `form-control`
- [ ] BootstrapSelect renders with `form-select`
- [ ] BootstrapDateTimeInput renders with datetime-local
- [ ] NO hardcoded `attrs={'class': '...'}`

### 3. Template Tags ⬜
- [ ] `{% status_badge %}` renders colored badges
- [ ] `{% format_datetime %}` formats dates consistently
- [ ] `{% render_pagination %}` renders pagination UI

### 4. Template Components ⬜
- [ ] `{% include 'components/card.html' %}` works
- [ ] Card header, body structure correct
- [ ] Alert component displays messages

### 5. Permission Decorators ⬜
- [ ] `@login_required` blocks anonymous users
- [ ] `@staff_required` blocks patients
- [ ] Staff and admin can create announcements

### 6. Constants ⬜
- [ ] SUCCESS_ANNOUNCEMENT_CREATED used in views
- [ ] ANNOUNCEMENTS_PER_PAGE controls pagination
- [ ] All magic strings centralized in constants.py

---

## Known Issues

**Unicode Encoding Warnings:**
- Windows console cannot display emoji characters in logs
- Non-fatal, does not affect functionality
- Emojis: 🔥 (U+1F525), ✅ (U+2705)

**Workaround:** Ignore logging errors, server runs normally

---

## Next Steps After Testing

1. **If all tests pass:**
   - Mark module as production-ready
   - Use as reference for other modules
   - Document any findings

2. **If tests fail:**
   - Document specific failures
   - Fix issues
   - Re-test

3. **After validation:**
   - Consider creating automated tests (test_announcements.py)
   - Add to CI/CD pipeline
   - Create API endpoints if needed

---

## Testing Checklist for Developers

When testing any module with foundation components:

- [ ] All models inherit from base models (no manual timestamps)
- [ ] All forms use widget library (no hardcoded classes)
- [ ] All templates use template tags (consistent formatting)
- [ ] All templates use components (no HTML duplication)
- [ ] Permission decorators applied (role-based access)
- [ ] Constants used instead of magic strings
- [ ] Mobile responsive design verified
- [ ] Code follows DRY principles

---

**Status:** Ready for Manual Testing
**Prerequisites:** Development server running, test users created
**Estimated Time:** 30-45 minutes for complete test suite

---

*Created with Claude Code demonstrating foundation components*
*Test module: announcements*
*Foundation files: common/models.py, common/widgets.py, common/templatetags/common_tags.py, templates/components/*
