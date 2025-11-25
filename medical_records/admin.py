from django.contrib import admin
from .models import (
    MedicalCondition, Allergy, Medication, Vaccination,
    Surgery, FamilyHistory, MedicalDocument, LifestyleInformation, COVIDRiskScore
)


@admin.register(MedicalCondition)
class MedicalConditionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'condition_name', 'severity', 'status', 'diagnosed_date', 'increases_covid_risk']
    list_filter = ['severity', 'status', 'increases_covid_risk', 'diagnosed_date']
    search_fields = ['condition_name', 'patient__user__username', 'patient__user__first_name', 'patient__user__last_name']
    date_hierarchy = 'diagnosed_date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'condition_name', 'icd_code')
        }),
        ('Classification', {
            'fields': ('severity', 'status', 'increases_covid_risk')
        }),
        ('Timeline', {
            'fields': ('diagnosed_date', 'resolved_date')
        }),
        ('Details', {
            'fields': ('description', 'symptoms', 'treatment', 'notes')
        }),
        ('Metadata', {
            'fields': ('diagnosed_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['patient', 'allergen', 'allergy_type', 'severity', 'is_active', 'verified_by_doctor']
    list_filter = ['allergy_type', 'severity', 'is_active', 'verified_by_doctor']
    search_fields = ['allergen', 'patient__user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medication_name', 'dosage', 'status', 'start_date']
    list_filter = ['status', 'start_date']
    search_fields = ['medication_name', 'patient__user__username', 'purpose']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Vaccination)
class VaccinationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'vaccine_name', 'dose_number', 'administered_date', 'adverse_reaction']
    list_filter = ['vaccine_name', 'administered_date', 'adverse_reaction']
    search_fields = ['patient__user__username', 'vaccine_brand', 'location']
    date_hierarchy = 'administered_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Surgery)
class SurgeryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'surgery_name', 'surgery_date', 'hospital']
    list_filter = ['surgery_date']
    search_fields = ['surgery_name', 'patient__user__username', 'surgeon_name', 'hospital']
    date_hierarchy = 'surgery_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FamilyHistory)
class FamilyHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'relationship', 'condition', 'age_at_diagnosis', 'is_deceased']
    list_filter = ['relationship', 'is_deceased']
    search_fields = ['patient__user__username', 'condition']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'document_type', 'document_date', 'is_sensitive', 'version']
    list_filter = ['document_type', 'is_sensitive', 'document_date', 'created_at']
    search_fields = ['title', 'patient__user__username', 'extracted_text']
    date_hierarchy = 'document_date'
    readonly_fields = ['document_id', 'file_size', 'created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('patient', 'document_type', 'title', 'description')
        }),
        ('File', {
            'fields': ('file', 'file_size', 'document_date')
        }),
        ('Access & Version Control', {
            'fields': ('is_sensitive', 'version', 'replaces')
        }),
        ('OCR & Search', {
            'fields': ('extracted_text',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('document_id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LifestyleInformation)
class LifestyleInformationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'smoking_status', 'alcohol_use', 'exercise_level', 'occupational_exposure_risk']
    list_filter = ['smoking_status', 'alcohol_use', 'exercise_level', 'occupational_exposure_risk']
    search_fields = ['patient__user__username', 'occupation']
    readonly_fields = ['updated_at']


@admin.register(COVIDRiskScore)
class COVIDRiskScoreAdmin(admin.ModelAdmin):
    list_display = ['patient', 'risk_level', 'total_score', 'created_at']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['patient__user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

    fieldsets = (
        ('Patient & Risk Level', {
            'fields': ('patient', 'risk_level', 'total_score')
        }),
        ('Score Breakdown', {
            'fields': ('age_score', 'comorbidity_score', 'lifestyle_score', 'vaccination_score')
        }),
        ('Details', {
            'fields': ('risk_factors', 'recommendations')
        }),
        ('Metadata', {
            'fields': ('calculated_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
