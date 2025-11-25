"""
Custom Django system checks to enforce foundation-components skill compliance.

These checks run automatically during:
- `python manage.py check`
- `python manage.py runserver`
- `python manage.py migrate`

Any violations will be reported as warnings or errors.
"""

from django.apps import apps
from django.core.checks import Warning, Error, register, Tags


# Base models that all models should inherit from
REQUIRED_BASE_FIELDS = {
    'created_at': 'TimeStampedModel',
    'updated_at': 'TimeStampedModel',
}

# Models that are exempt from checks (Django built-in, third-party, etc.)
EXEMPT_APPS = {
    'admin', 'auth', 'contenttypes', 'sessions', 'token_blacklist',
    'django_celery_beat', 'django_celery_results',
}

# Models that are intentionally exempt (abstract models, through tables, etc.)
EXEMPT_MODELS = {
    'common.TimeStampedModel',
    'common.SoftDeleteModel',
    'common.AuditableModel',
    'common.FullAuditModel',
    'common.TimeStampedSoftDeleteModel',
    'common.TimeStampedAuditableModel',
}


@register(Tags.models)
def check_models_inherit_base(app_configs, **kwargs):
    """
    Check that all models inherit from TimeStampedModel or its subclasses.

    This enforces the foundation-components skill requirement that all models
    must have created_at and updated_at fields from abstract base models.
    """
    errors = []

    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = f"{app_label}.{model.__name__}"

        # Skip exempt apps and models
        if app_label in EXEMPT_APPS:
            continue
        if model_name in EXEMPT_MODELS:
            continue
        if model._meta.abstract:
            continue

        # Check for required fields from TimeStampedModel
        field_names = {f.name for f in model._meta.get_fields()}

        missing_fields = []
        for field, base_model in REQUIRED_BASE_FIELDS.items():
            if field not in field_names:
                missing_fields.append(f"'{field}' (from {base_model})")

        if missing_fields:
            errors.append(
                Warning(
                    f"Model '{model_name}' is missing required fields: {', '.join(missing_fields)}",
                    hint=(
                        f"Inherit from 'common.models.TimeStampedModel' or one of its subclasses "
                        f"(FullAuditModel, TimeStampedSoftDeleteModel, TimeStampedAuditableModel). "
                        f"See foundation-components skill in CLAUDE.md."
                    ),
                    obj=model,
                    id='common.W001',
                )
            )

    return errors


@register(Tags.models)
def check_soft_delete_models(app_configs, **kwargs):
    """
    Check that models with is_deleted field also have proper manager setup.

    Models using SoftDeleteModel should have both 'objects' (active only)
    and 'all_objects' (including deleted) managers.
    """
    errors = []

    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = f"{app_label}.{model.__name__}"

        # Skip exempt apps
        if app_label in EXEMPT_APPS:
            continue
        if model._meta.abstract:
            continue

        field_names = {f.name for f in model._meta.get_fields()}

        # If model has is_deleted, it should have all_objects manager
        if 'is_deleted' in field_names:
            if not hasattr(model, 'all_objects'):
                errors.append(
                    Warning(
                        f"Model '{model_name}' has 'is_deleted' field but missing 'all_objects' manager",
                        hint=(
                            f"Inherit from 'common.models.SoftDeleteModel' or 'common.models.FullAuditModel' "
                            f"to get proper soft-delete support with ActiveManager. "
                            f"See foundation-components skill in CLAUDE.md."
                        ),
                        obj=model,
                        id='common.W002',
                    )
                )

    return errors


@register(Tags.models)
def check_audit_fields_consistency(app_configs, **kwargs):
    """
    Check that audit fields are used consistently.

    If a model has created_by, it should also have updated_by (AuditableModel).
    If a model has deleted_by, it should also have is_deleted and deleted_at (SoftDeleteModel).
    """
    errors = []

    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = f"{app_label}.{model.__name__}"

        # Skip exempt apps
        if app_label in EXEMPT_APPS:
            continue
        if model._meta.abstract:
            continue

        field_names = {f.name for f in model._meta.get_fields()}

        # Check AuditableModel consistency
        has_created_by = 'created_by' in field_names
        has_updated_by = 'updated_by' in field_names

        if has_created_by and not has_updated_by:
            errors.append(
                Warning(
                    f"Model '{model_name}' has 'created_by' but missing 'updated_by'",
                    hint=(
                        f"Use 'common.models.AuditableModel' or 'common.models.FullAuditModel' "
                        f"for consistent audit trail. See foundation-components skill."
                    ),
                    obj=model,
                    id='common.W003',
                )
            )

        # Check SoftDeleteModel consistency
        soft_delete_fields = {'is_deleted', 'deleted_at', 'deleted_by'}
        present_soft_delete = soft_delete_fields & field_names

        if present_soft_delete and present_soft_delete != soft_delete_fields:
            missing = soft_delete_fields - present_soft_delete
            errors.append(
                Warning(
                    f"Model '{model_name}' has incomplete soft-delete fields. Missing: {missing}",
                    hint=(
                        f"Use 'common.models.SoftDeleteModel' or 'common.models.FullAuditModel' "
                        f"for complete soft-delete support. See foundation-components skill."
                    ),
                    obj=model,
                    id='common.W004',
                )
            )

    return errors
