from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    # Medical conditions
    path('conditions/', views.condition_list, name='condition_list'),
    path('conditions/add/', views.add_condition, name='add_condition'),
    path('conditions/<int:condition_id>/edit/', views.edit_condition, name='edit_condition'),
    path('conditions/<int:condition_id>/delete/', views.delete_condition, name='delete_condition'),

    # Allergies
    path('allergies/', views.allergy_list, name='allergy_list'),
    path('allergies/add/', views.add_allergy, name='add_allergy'),
    path('allergies/<int:allergy_id>/edit/', views.edit_allergy, name='edit_allergy'),

    # Medications
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/add/', views.add_medication, name='add_medication'),
    path('medications/<int:medication_id>/edit/', views.edit_medication, name='edit_medication'),

    # Vaccinations
    path('vaccinations/', views.vaccination_list, name='vaccination_list'),
    path('vaccinations/add/', views.add_vaccination, name='add_vaccination'),

    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/<uuid:document_id>/', views.view_document, name='view_document'),
    path('documents/<uuid:document_id>/download/', views.download_document, name='download_document'),

    # Medical summary
    path('summary/<int:patient_id>/', views.medical_summary, name='medical_summary'),

    # Risk assessment
    path('risk-assessment/<int:patient_id>/', views.calculate_risk_score, name='calculate_risk_score'),
]
