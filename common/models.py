"""
Abstract base models for the COVID-19 Detection application.

These models provide common functionality and fields that can be inherited
by all other models in the application to ensure consistency and reduce code duplication.

Usage:
    from common.models import TimeStampedModel, SoftDeleteModel, AuditableModel

    class MyModel(TimeStampedModel):
        # Your model fields here
        pass
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides automatic timestamp fields.

    Adds created_at and updated_at fields that are automatically
    managed by Django. All models should inherit from this to
    maintain consistent timestamp tracking.

    Fields:
        created_at (DateTimeField): Automatically set when object is created
        updated_at (DateTimeField): Automatically updated when object is saved

    Example:
        class Appointment(TimeStampedModel):
            patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
            scheduled_date = models.DateTimeField()
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']  # Default ordering: newest first


class SoftDeleteModel(models.Model):
    """
    Abstract base model that provides soft delete functionality.

    Instead of permanently deleting records from the database,
    this model marks them as deleted. This allows for data recovery
    and maintains referential integrity.

    Fields:
        is_deleted (BooleanField): Whether the record is deleted
        deleted_at (DateTimeField): Timestamp when record was deleted
        deleted_by (ForeignKey): User who deleted the record

    Methods:
        soft_delete(user): Mark the record as deleted
        restore(): Restore a soft-deleted record

    Example:
        appointment = Appointment.objects.get(id=1)
        appointment.soft_delete(request.user)  # Soft delete
        appointment.restore()  # Restore
    """
    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates if the record has been soft deleted"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the record was deleted"
    )
    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        help_text="User who deleted this record"
    )

    class Meta:
        abstract = True

    def soft_delete(self, user: User = None) -> None:
        """
        Mark this record as deleted without removing it from the database.

        Args:
            user (User, optional): The user performing the deletion
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def restore(self) -> None:
        """
        Restore a soft-deleted record.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])


class AuditableModel(models.Model):
    """
    Abstract base model that provides audit trail functionality.

    Tracks who created and last updated a record. Useful for
    compliance and accountability in medical/healthcare applications.

    Fields:
        created_by (ForeignKey): User who created the record
        updated_by (ForeignKey): User who last updated the record

    Example:
        class MedicalRecord(TimeStampedModel, AuditableModel):
            patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
            diagnosis = models.TextField()
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )

    class Meta:
        abstract = True


class ActiveManager(models.Manager):
    """
    Custom manager that excludes soft-deleted records.

    Use this manager to automatically filter out deleted records
    from all queries.

    Example:
        class Appointment(TimeStampedModel, SoftDeleteModel):
            # ... fields ...

            objects = ActiveManager()  # Only returns non-deleted
            all_objects = models.Manager()  # Returns all including deleted

        # Usage:
        active_appointments = Appointment.objects.all()  # Excludes deleted
        all_appointments = Appointment.all_objects.all()  # Includes deleted
    """
    def get_queryset(self):
        """Return only non-deleted records."""
        return super().get_queryset().filter(is_deleted=False)


class TimeStampedAuditableModel(TimeStampedModel, AuditableModel):
    """
    Combination of TimeStampedModel and AuditableModel.

    Provides both automatic timestamps and audit trail tracking.
    This is the recommended base model for most application models.

    Fields:
        - created_at (from TimeStampedModel)
        - updated_at (from TimeStampedModel)
        - created_by (from AuditableModel)
        - updated_by (from AuditableModel)

    Example:
        class Prescription(TimeStampedAuditableModel):
            patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
            medication = models.CharField(max_length=200)
            dosage = models.CharField(max_length=100)
    """
    class Meta:
        abstract = True


class TimeStampedSoftDeleteModel(TimeStampedModel, SoftDeleteModel):
    """
    Combination of TimeStampedModel and SoftDeleteModel.

    Provides both automatic timestamps and soft delete functionality.
    Use this for models where you want to preserve deletion history.

    Fields:
        - created_at (from TimeStampedModel)
        - updated_at (from TimeStampedModel)
        - is_deleted (from SoftDeleteModel)
        - deleted_at (from SoftDeleteModel)
        - deleted_by (from SoftDeleteModel)

    Managers:
        - objects: Returns only active (non-deleted) records
        - all_objects: Returns all records including deleted

    Example:
        class Appointment(TimeStampedSoftDeleteModel):
            patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
            scheduled_date = models.DateTimeField()

            objects = ActiveManager()  # Only non-deleted
            all_objects = models.Manager()  # All records
    """
    objects = ActiveManager()  # Default manager excludes deleted
    all_objects = models.Manager()  # Manager that includes deleted

    class Meta:
        abstract = True


class FullAuditModel(TimeStampedModel, AuditableModel, SoftDeleteModel):
    """
    Complete audit trail model with timestamps, user tracking, and soft delete.

    This is the most comprehensive base model, providing:
    - Automatic timestamps (created_at, updated_at)
    - User audit trail (created_by, updated_by)
    - Soft delete functionality (is_deleted, deleted_at, deleted_by)

    Use this for critical data that requires complete audit trail.

    Fields:
        - created_at, updated_at (TimeStampedModel)
        - created_by, updated_by (AuditableModel)
        - is_deleted, deleted_at, deleted_by (SoftDeleteModel)

    Managers:
        - objects: Returns only active (non-deleted) records
        - all_objects: Returns all records including deleted

    Example:
        class MedicalRecord(FullAuditModel):
            patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
            diagnosis = models.TextField()
            treatment_plan = models.TextField()

            objects = ActiveManager()
            all_objects = models.Manager()
    """
    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


# Usage Guidelines:
#
# 1. For most models: Use TimeStampedModel
#    - Simple, provides created_at and updated_at
#    - Example: Blog posts, comments, simple data
#
# 2. For models requiring audit trail: Use TimeStampedAuditableModel
#    - Tracks who created and updated
#    - Example: Medical records, financial data
#
# 3. For models that might be deleted: Use TimeStampedSoftDeleteModel
#    - Allows soft deletion and recovery
#    - Example: Appointments, user profiles
#
# 4. For critical data: Use FullAuditModel
#    - Complete audit trail with soft delete
#    - Example: Patient records, prescriptions, medical reports
