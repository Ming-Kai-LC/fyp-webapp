# common/mixins.py
"""
Reusable view mixins for the COVID-19 Detection application.

Provides class-based view (CBV) mixins for common functionality:
- Role-based access control
- Page title management
- Form handling with multiple forms
- Profile completion checks
- Audit logging

Usage:
    from common.mixins import RoleRequiredMixin, PageTitleMixin, MultiFormMixin

    class MyView(RoleRequiredMixin, PageTitleMixin, TemplateView):
        allowed_roles = ['admin', 'staff']
        page_title = 'Dashboard'
"""

import logging
from typing import Dict, Any, List, Optional, Type

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import View
from django.views.generic.edit import FormMixin

logger = logging.getLogger(__name__)


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin that requires user to have specific role(s).

    Attributes:
        allowed_roles: List of allowed roles (e.g., ['admin', 'staff'])
        role_redirect_url: URL to redirect if role check fails
        role_permission_denied: If True, raises 403 instead of redirecting

    Usage:
        class AdminOnlyView(RoleRequiredMixin, TemplateView):
            allowed_roles = ['admin']
            template_name = 'admin/dashboard.html'

        class StaffView(RoleRequiredMixin, TemplateView):
            allowed_roles = ['admin', 'staff']
            template_name = 'staff/dashboard.html'
    """

    allowed_roles: List[str] = []
    role_redirect_url: str = "home"
    role_permission_denied: bool = False

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Check user role before dispatching to view."""
        # First check if user is authenticated (via LoginRequiredMixin)
        response = super().dispatch(request, *args, **kwargs)

        # If not authenticated, LoginRequiredMixin handles redirect
        if not request.user.is_authenticated:
            return response

        # Check role
        if not self._check_role(request.user):
            return self._handle_no_permission(request)

        return response

    def _check_role(self, user) -> bool:
        """Check if user has one of the allowed roles."""
        if not self.allowed_roles:
            return True  # No role restriction

        try:
            profile = user.profile
            user_role = profile.role

            # Check if user's role is in allowed roles
            if user_role in self.allowed_roles:
                return True

            # Special case: admin can access everything
            if profile.is_admin():
                return True

            return False

        except AttributeError:
            logger.warning(f"User {user.username} has no profile")
            return False

    def _handle_no_permission(self, request: HttpRequest) -> HttpResponse:
        """Handle case when user doesn't have required role."""
        if self.role_permission_denied:
            raise PermissionDenied("You don't have permission to access this page.")

        messages.error(request, "You don't have permission to access this page.")
        return redirect(self.role_redirect_url)


class AdminRequiredMixin(RoleRequiredMixin):
    """Shortcut mixin for admin-only views."""

    allowed_roles = ["admin"]


class StaffRequiredMixin(RoleRequiredMixin):
    """Shortcut mixin for staff and admin views."""

    allowed_roles = ["admin", "staff"]


class PatientRequiredMixin(RoleRequiredMixin):
    """Shortcut mixin for patient-only views."""

    allowed_roles = ["patient"]


class PageTitleMixin:
    """
    Mixin that adds page title to context.

    Attributes:
        page_title: Static page title
        page_subtitle: Optional subtitle

    Usage:
        class DashboardView(PageTitleMixin, TemplateView):
            page_title = 'Dashboard'
            page_subtitle = 'Overview of your activity'
    """

    page_title: str = ""
    page_subtitle: str = ""

    def get_page_title(self) -> str:
        """Get page title. Override for dynamic titles."""
        return self.page_title

    def get_page_subtitle(self) -> str:
        """Get page subtitle. Override for dynamic subtitles."""
        return self.page_subtitle

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.get_page_title()
        context["page_subtitle"] = self.get_page_subtitle()
        return context


class MultiFormMixin:
    """
    Mixin for handling multiple forms in a single view.

    Attributes:
        form_classes: Dict mapping form names to form classes
        initial: Dict mapping form names to initial data dicts
        success_url: URL to redirect on successful form submission
        form_type_field: Name of the hidden field identifying which form was submitted

    Usage:
        class ProfileView(MultiFormMixin, TemplateView):
            form_classes = {
                'basic_info': UserBasicInfoForm,
                'patient_info': PatientProfileForm,
                'picture': ProfilePictureForm,
            }
            form_type_field = 'form_type'
            success_url = reverse_lazy('detection:user_profile')

            def get_form_kwargs(self, form_name):
                kwargs = super().get_form_kwargs(form_name)
                if form_name == 'basic_info':
                    kwargs['user'] = self.request.user
                return kwargs

            def form_valid(self, form_name, form):
                form.save()
                messages.success(self.request, 'Saved!')
                return super().form_valid(form_name, form)
    """

    form_classes: Dict[str, Type] = {}
    initial: Dict[str, Dict[str, Any]] = {}
    success_url: Optional[str] = None
    form_type_field: str = "form_type"

    def get_form_classes(self) -> Dict[str, Type]:
        """Return the dict of form classes. Override for dynamic forms."""
        return self.form_classes

    def get_form_kwargs(self, form_name: str) -> Dict[str, Any]:
        """
        Return kwargs for instantiating a specific form.
        Override to provide custom kwargs per form.
        """
        kwargs = {}

        # Add data and files if this form was submitted
        if self.request.method == "POST":
            submitted_form = self.request.POST.get(self.form_type_field)
            if submitted_form == form_name:
                kwargs["data"] = self.request.POST
                kwargs["files"] = self.request.FILES

        # Add initial data if provided
        initial = self.get_initial(form_name)
        if initial:
            kwargs["initial"] = initial

        return kwargs

    def get_initial(self, form_name: str) -> Dict[str, Any]:
        """Get initial data for a specific form."""
        return self.initial.get(form_name, {})

    def get_form(self, form_name: str) -> Any:
        """Instantiate and return a specific form."""
        form_classes = self.get_form_classes()
        form_class = form_classes.get(form_name)

        if not form_class:
            return None

        return form_class(**self.get_form_kwargs(form_name))

    def get_forms(self) -> Dict[str, Any]:
        """Instantiate and return all forms."""
        return {
            name: self.get_form(name) for name in self.get_form_classes().keys()
        }

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add all forms to context."""
        context = super().get_context_data(**kwargs)

        # Add forms to context with their names
        forms = self.get_forms()
        for name, form in forms.items():
            context[f"{name}_form"] = form

        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Handle POST request by validating the submitted form."""
        form_type = request.POST.get(self.form_type_field)

        if form_type and form_type in self.get_form_classes():
            form = self.get_form(form_type)
            if form and form.is_valid():
                return self.form_valid(form_type, form)
            else:
                return self.form_invalid(form_type, form)

        return self.get(request, *args, **kwargs)

    def form_valid(self, form_name: str, form: Any) -> HttpResponse:
        """Handle valid form submission. Override to add custom logic."""
        if hasattr(form, "save"):
            form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form_name: str, form: Any) -> HttpResponse:
        """Handle invalid form submission."""
        return self.render_to_response(self.get_context_data())

    def get_success_url(self) -> str:
        """Return the URL to redirect to after successful form submission."""
        if self.success_url:
            return self.success_url
        return self.request.path


class ProfileContextMixin:
    """
    Mixin that adds user profile data to context.

    Adds:
        - profile: UserProfile instance
        - is_patient, is_staff, is_admin: Role booleans
        - completion: Profile completion data

    Usage:
        class MyView(ProfileContextMixin, TemplateView):
            template_name = 'my_template.html'
    """

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add profile data to context."""
        context = super().get_context_data(**kwargs)

        user = self.request.user
        if user.is_authenticated:
            try:
                profile = user.profile
                context["profile"] = profile
                context["is_patient"] = profile.is_patient()
                context["is_staff"] = profile.is_staff()
                context["is_admin"] = profile.is_admin()

                # Add completion data if ProfileService is available
                try:
                    from detection.services import ProfileService

                    context["completion"] = ProfileService.get_profile_completion(user)
                except ImportError:
                    pass

            except AttributeError:
                pass

        return context


class AuditMixin:
    """
    Mixin that logs view access for audit purposes.

    Usage:
        class SensitiveDataView(AuditMixin, DetailView):
            model = PatientRecord
            audit_action = 'view_patient_record'
    """

    audit_action: str = ""
    audit_log_request: bool = True

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Log access before dispatching to view."""
        if self.audit_log_request and request.user.is_authenticated:
            self._log_access(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def _log_access(self, request: HttpRequest, *args, **kwargs) -> None:
        """Log the access. Override for custom logging."""
        action = self.audit_action or self.__class__.__name__
        logger.info(
            f"AUDIT: User {request.user.username} accessed {action} "
            f"[IP: {self._get_client_ip(request)}]"
        )

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class SuccessMessageMixin:
    """
    Mixin that adds success message on form submission.

    Attributes:
        success_message: Message to display on success

    Usage:
        class MyFormView(SuccessMessageMixin, FormView):
            success_message = 'Your changes have been saved!'
    """

    success_message: str = "Changes saved successfully!"

    def get_success_message(self) -> str:
        """Get success message. Override for dynamic messages."""
        return self.success_message

    def form_valid(self, form) -> HttpResponse:
        """Add success message before redirecting."""
        messages.success(self.request, self.get_success_message())
        return super().form_valid(form)


class FormValidationMixin:
    """
    Mixin that adds enhanced form validation error handling.

    Adds error messages to Django messages framework for display.

    Usage:
        class MyFormView(FormValidationMixin, FormView):
            pass
    """

    show_field_errors_in_messages: bool = False
    generic_error_message: str = "Please correct the errors below."

    def form_invalid(self, form) -> HttpResponse:
        """Add error message on form invalid."""
        if self.show_field_errors_in_messages:
            for field, errors in form.errors.items():
                for error in errors:
                    field_name = form.fields.get(field, field)
                    if hasattr(field_name, "label"):
                        field_name = field_name.label
                    messages.error(self.request, f"{field_name}: {error}")
        else:
            messages.error(self.request, self.generic_error_message)

        return super().form_invalid(form)
