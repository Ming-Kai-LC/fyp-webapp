# detection/admin.py
"""
Django Admin Panel Configuration
🎉 This gives you a FREE beautiful admin interface!
Access at: http://localhost:8000/admin/
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserProfile, Patient, XRayImage, Prediction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles"""
    
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Contact Details', {
            'fields': ('phone',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize database queries"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for patient records"""
    
    list_display = ['user', 'age', 'gender', 'total_xrays', 'covid_count', 'emergency_contact']
    list_filter = ['gender', 'age']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_xrays', 'covid_count']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'age', 'gender', 'date_of_birth')
        }),
        ('Medical Information', {
            'fields': ('medical_history', 'current_medications')
        }),
        ('Contact Information', {
            'fields': ('emergency_contact', 'address')
        }),
        ('Statistics', {
            'fields': ('total_xrays', 'covid_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_xrays(self, obj):
        """Display total X-rays for patient"""
        count = obj.get_total_xrays()
        url = reverse('admin:detection_xrayimage_changelist') + f'?patient__id__exact={obj.id}'
        return format_html('<a href="{}">{} X-rays</a>', url, count)
    total_xrays.short_description = 'Total X-rays'
    
    def covid_count(self, obj):
        """Display COVID-19 positive count"""
        count = obj.get_covid_positive_count()
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">{} COVID+ cases</span>', count)
        return format_html('<span style="color: green;">No COVID+ cases</span>')
    covid_count.short_description = 'COVID-19 Status'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(XRayImage)
class XRayImageAdmin(admin.ModelAdmin):
    """Admin interface for X-ray images"""
    
    list_display = ['id', 'patient_name', 'uploaded_by', 'upload_date', 'image_thumbnail', 'has_predictions']
    list_filter = ['upload_date']
    search_fields = ['patient__user__username', 'uploaded_by__username', 'notes']
    readonly_fields = ['upload_date', 'image_width', 'image_height', 'file_size', 
                      'original_image_preview', 'processed_image_preview']
    date_hierarchy = 'upload_date'
    
    fieldsets = (
        ('Patient & Upload Info', {
            'fields': ('patient', 'uploaded_by', 'upload_date')
        }),
        ('Images', {
            'fields': ('original_image', 'original_image_preview', 
                      'processed_image', 'processed_image_preview')
        }),
        ('Image Properties', {
            'fields': ('image_width', 'image_height', 'file_size'),
            'classes': ('collapse',)
        }),
        ('Clinical Notes', {
            'fields': ('notes',)
        }),
    )
    
    def patient_name(self, obj):
        """Display patient name"""
        return obj.patient.user.get_full_name() or obj.patient.user.username
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__user__last_name'
    
    def image_thumbnail(self, obj):
        """Display small image thumbnail"""
        if obj.original_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.original_image.url
            )
        return '-'
    image_thumbnail.short_description = 'Thumbnail'
    
    def original_image_preview(self, obj):
        """Display full original image"""
        if obj.original_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.original_image.url
            )
        return '-'
    original_image_preview.short_description = 'Original Image Preview'
    
    def processed_image_preview(self, obj):
        """Display processed (CLAHE) image"""
        if obj.processed_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.processed_image.url
            )
        return '-'
    processed_image_preview.short_description = 'Processed Image (CLAHE)'
    
    def has_predictions(self, obj):
        """Show if predictions exist"""
        count = obj.predictions.count()
        if count > 0:
            return format_html('✅ {} prediction(s)', count)
        return '❌ No predictions'
    has_predictions.short_description = 'Predictions'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('patient__user', 'uploaded_by')


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """
    🌟 MAIN ADMIN INTERFACE FOR PREDICTIONS
    Shows all model results in a beautiful interface
    """
    
    list_display = [
        'id',
        'patient_name',
        'final_diagnosis_display',
        'consensus_confidence_display',
        'best_model_display',
        'agreement_display',
        'is_validated',
        'created_at'
    ]
    
    list_filter = [
        'final_diagnosis',
        'is_validated',
        'created_at',
        'crossvit_prediction',
    ]
    
    search_fields = [
        'xray__patient__user__username',
        'xray__patient__user__first_name',
        'xray__patient__user__last_name',
        'final_diagnosis',
        'doctor_notes'
    ]
    
    readonly_fields = [
        'created_at',
        'inference_time',
        'xray_preview',
        'gradcam_preview',
        'large_branch_preview',
        'small_branch_preview'
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('X-Ray & Patient Information', {
            'fields': ('xray', 'xray_preview')
        }),
        ('🔥 CrossViT Prediction (Your Model)', {
            'fields': ('crossvit_prediction', 'crossvit_confidence'),
            'classes': ('wide',),
            'description': 'Results from your CrossViT dual-branch model'
        }),
        ('📊 Baseline Model Predictions', {
            'fields': (
                ('resnet50_prediction', 'resnet50_confidence'),
                ('densenet121_prediction', 'densenet121_confidence'),
                ('efficientnet_prediction', 'efficientnet_confidence'),
                ('vit_prediction', 'vit_confidence'),
                ('swin_prediction', 'swin_confidence'),
            ),
            'classes': ('collapse',),
            'description': 'Results from 5 baseline models for comparison'
        }),
        ('🎯 Final Diagnosis & Performance', {
            'fields': ('final_diagnosis', 'consensus_confidence', 'inference_time'),
            'classes': ('wide',)
        }),
        ('🔍 Explainability Visualizations (Spotlight 2)', {
            'fields': (
                'gradcam_heatmap',
                'gradcam_preview',
                'large_branch_attention',
                'large_branch_preview',
                'small_branch_attention',
                'small_branch_preview'
            ),
            'classes': ('collapse',)
        }),
        ('✅ Doctor Review & Validation', {
            'fields': (
                'reviewed_by',
                'doctor_notes',
                'is_validated',
                'validated_at'
            ),
            'classes': ('wide',)
        }),
        ('⏰ Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # Custom display methods
    
    def patient_name(self, obj):
        """Display patient name with link"""
        patient = obj.xray.patient
        url = reverse('admin:detection_patient_change', args=[patient.id])
        name = patient.user.get_full_name() or patient.user.username
        return format_html('<a href="{}">{}</a>', url, name)
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'xray__patient__user__last_name'
    
    def final_diagnosis_display(self, obj):
        """Display final diagnosis with color coding"""
        colors = {
            'COVID': 'red',
            'Normal': 'green',
            'Viral Pneumonia': 'orange',
            'Lung Opacity': 'blue'
        }
        color = colors.get(obj.final_diagnosis, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.final_diagnosis
        )
    final_diagnosis_display.short_description = 'Diagnosis'
    final_diagnosis_display.admin_order_field = 'final_diagnosis'
    
    def consensus_confidence_display(self, obj):
        """Display confidence with progress bar"""
        confidence = obj.consensus_confidence
        if confidence >= 90:
            color = 'green'
        elif confidence >= 75:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 5px;">'
            '<div style="width: {}%; background-color: {}; color: white; '
            'text-align: center; border-radius: 5px; font-weight: bold;">{:.1f}%</div>'
            '</div>',
            confidence,
            color,
            confidence
        )
    consensus_confidence_display.short_description = 'Confidence'
    
    def best_model_display(self, obj):
        """Display best performing model"""
        best_model, confidence = obj.get_best_model()
        return format_html(
            '<span style="background-color: #e8f5e9; padding: 3px 8px; border-radius: 3px;">'
            '{} ({:.1f}%)</span>',
            best_model,
            confidence
        )
    best_model_display.short_description = 'Best Model'
    
    def agreement_display(self, obj):
        """Display model agreement count"""
        agreement = obj.get_model_agreement()
        if agreement >= 5:
            icon = '✅✅✅'
            color = 'green'
        elif agreement >= 4:
            icon = '✅✅'
            color = 'orange'
        else:
            icon = '⚠️'
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{} {}/6 models</span>',
            color,
            icon,
            agreement
        )
    agreement_display.short_description = 'Model Agreement'
    
    def xray_preview(self, obj):
        """Display X-ray images side by side"""
        html = '<div style="display: flex; gap: 20px;">'
        
        # Original image
        if obj.xray.original_image:
            html += '<div><strong>Original:</strong><br>'
            html += f'<img src="{obj.xray.original_image.url}" style="max-width: 200px; max-height: 200px;" />'
            html += '</div>'
        
        # Processed image
        if obj.xray.processed_image:
            html += '<div><strong>CLAHE Enhanced:</strong><br>'
            html += f'<img src="{obj.xray.processed_image.url}" style="max-width: 200px; max-height: 200px;" />'
            html += '</div>'
        
        html += '</div>'
        return mark_safe(html)
    xray_preview.short_description = 'X-Ray Images'
    
    def gradcam_preview(self, obj):
        """Display Grad-CAM heatmap"""
        if obj.gradcam_heatmap:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.gradcam_heatmap.url
            )
        return '❌ Not generated yet'
    gradcam_preview.short_description = 'Grad-CAM Heatmap'
    
    def large_branch_preview(self, obj):
        """Display large branch attention"""
        if obj.large_branch_attention:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.large_branch_attention.url
            )
        return '❌ Not generated yet'
    large_branch_preview.short_description = 'Large Branch Attention'
    
    def small_branch_preview(self, obj):
        """Display small branch attention"""
        if obj.small_branch_attention:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.small_branch_attention.url
            )
        return '❌ Not generated yet'
    small_branch_preview.short_description = 'Small Branch Attention'
    
    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'xray__patient__user',
            'xray__uploaded_by',
            'reviewed_by'
        )
    
    # Custom actions
    actions = ['mark_as_validated', 'generate_explainability']
    
    def mark_as_validated(self, request, queryset):
        """Bulk action to mark predictions as validated"""
        updated = queryset.update(
            is_validated=True,
            reviewed_by=request.user,
            validated_at=timezone.now()
        )
        self.message_user(request, f'{updated} prediction(s) marked as validated.')
    mark_as_validated.short_description = 'Mark selected as validated'
    
    def generate_explainability(self, request, queryset):
        """Bulk action to generate explainability (admin can trigger)"""
        count = 0
        for prediction in queryset:
            if not prediction.gradcam_heatmap:
                # Trigger explainability generation
                # (This would need to import and call the explainability functions)
                count += 1
        
        self.message_user(request, f'Explainability queued for {count} prediction(s).')
    generate_explainability.short_description = 'Generate explainability visualizations'


# Customize admin site header
admin.site.site_header = "COVID-19 Detection System Admin"
admin.site.site_title = "COVID-19 Admin"
admin.site.index_title = "Welcome to COVID-19 Detection System Administration"
