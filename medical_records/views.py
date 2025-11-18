"""
Medical Records Views - CRUD operations for patient medical data
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, FileResponse
from django.db.models import Q
from detection.models import Patient
from .models import (
    MedicalCondition, Allergy, Medication, Vaccination,
    Surgery, FamilyHistory, MedicalDocument, LifestyleInformation, COVIDRiskScore
)
from .forms import (
    MedicalConditionForm, AllergyForm, MedicationForm, VaccinationForm,
    SurgeryForm, FamilyHistoryForm, MedicalDocumentForm, LifestyleInformationForm
)
from .services import RiskAssessmentService


# ============== Medical Conditions ==============

@login_required
def condition_list(request):
    """List all medical conditions for the current patient"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    conditions = patient.medical_conditions.all()

    context = {
        'conditions': conditions,
        'patient': patient,
    }
    return render(request, 'medical_records/condition_list.html', context)


@login_required
def add_condition(request):
    """Add a new medical condition"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    if request.method == 'POST':
        form = MedicalConditionForm(request.POST)
        if form.is_valid():
            condition = form.save(commit=False)
            condition.patient = patient
            condition.diagnosed_by = request.user
            condition.save()
            messages.success(request, "Medical condition added successfully.")
            return redirect('medical_records:condition_list')
    else:
        form = MedicalConditionForm()

    context = {'form': form, 'patient': patient}
    return render(request, 'medical_records/condition_form.html', context)


@login_required
def edit_condition(request, condition_id):
    """Edit an existing medical condition"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    condition = get_object_or_404(MedicalCondition, id=condition_id, patient=patient)

    if request.method == 'POST':
        form = MedicalConditionForm(request.POST, instance=condition)
        if form.is_valid():
            form.save()
            messages.success(request, "Medical condition updated successfully.")
            return redirect('medical_records:condition_list')
    else:
        form = MedicalConditionForm(instance=condition)

    context = {'form': form, 'condition': condition, 'patient': patient}
    return render(request, 'medical_records/condition_form.html', context)


@login_required
def delete_condition(request, condition_id):
    """Delete a medical condition"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    condition = get_object_or_404(MedicalCondition, id=condition_id, patient=patient)

    if request.method == 'POST':
        condition.delete()
        messages.success(request, "Medical condition deleted successfully.")
        return redirect('medical_records:condition_list')

    context = {'condition': condition, 'patient': patient}
    return render(request, 'medical_records/condition_confirm_delete.html', context)


# ============== Allergies ==============

@login_required
def allergy_list(request):
    """List all allergies for the current patient"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    allergies = patient.allergies.filter(is_active=True)

    context = {
        'allergies': allergies,
        'patient': patient,
    }
    return render(request, 'medical_records/allergy_list.html', context)


@login_required
def add_allergy(request):
    """Add a new allergy"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    if request.method == 'POST':
        form = AllergyForm(request.POST)
        if form.is_valid():
            allergy = form.save(commit=False)
            allergy.patient = patient
            allergy.recorded_by = request.user
            allergy.save()
            messages.warning(request, f"Allergy to {allergy.allergen} added. Please inform medical staff.")
            return redirect('medical_records:allergy_list')
    else:
        form = AllergyForm()

    context = {'form': form, 'patient': patient}
    return render(request, 'medical_records/allergy_form.html', context)


@login_required
def edit_allergy(request, allergy_id):
    """Edit an existing allergy"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    allergy = get_object_or_404(Allergy, id=allergy_id, patient=patient)

    if request.method == 'POST':
        form = AllergyForm(request.POST, instance=allergy)
        if form.is_valid():
            form.save()
            messages.success(request, "Allergy information updated successfully.")
            return redirect('medical_records:allergy_list')
    else:
        form = AllergyForm(instance=allergy)

    context = {'form': form, 'allergy': allergy, 'patient': patient}
    return render(request, 'medical_records/allergy_form.html', context)


# ============== Medications ==============

@login_required
def medication_list(request):
    """List all medications for the current patient"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    medications = patient.medications.all()
    current_medications = medications.filter(status='current')
    past_medications = medications.exclude(status='current')

    context = {
        'current_medications': current_medications,
        'past_medications': past_medications,
        'patient': patient,
    }
    return render(request, 'medical_records/medication_list.html', context)


@login_required
def add_medication(request):
    """Add a new medication"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.patient = patient
            medication.recorded_by = request.user
            medication.save()
            messages.success(request, "Medication added successfully.")
            return redirect('medical_records:medication_list')
    else:
        form = MedicationForm()

    context = {'form': form, 'patient': patient}
    return render(request, 'medical_records/medication_form.html', context)


@login_required
def edit_medication(request, medication_id):
    """Edit an existing medication"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    medication = get_object_or_404(Medication, id=medication_id, patient=patient)

    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()
            messages.success(request, "Medication updated successfully.")
            return redirect('medical_records:medication_list')
    else:
        form = MedicationForm(instance=medication)

    context = {'form': form, 'medication': medication, 'patient': patient}
    return render(request, 'medical_records/medication_form.html', context)


# ============== Vaccinations ==============

@login_required
def vaccination_list(request):
    """List all vaccinations for the current patient"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    vaccinations = patient.vaccinations.all()
    covid_vaccinations = vaccinations.filter(vaccine_name__startswith='covid19')
    other_vaccinations = vaccinations.exclude(vaccine_name__startswith='covid19')

    context = {
        'covid_vaccinations': covid_vaccinations,
        'other_vaccinations': other_vaccinations,
        'patient': patient,
    }
    return render(request, 'medical_records/vaccination_list.html', context)


@login_required
def add_vaccination(request):
    """Add a new vaccination record"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    if request.method == 'POST':
        form = VaccinationForm(request.POST, request.FILES)
        if form.is_valid():
            vaccination = form.save(commit=False)
            vaccination.patient = patient
            vaccination.recorded_by = request.user
            vaccination.save()
            messages.success(request, "Vaccination record added successfully.")
            return redirect('medical_records:vaccination_list')
    else:
        form = VaccinationForm()

    context = {'form': form, 'patient': patient}
    return render(request, 'medical_records/vaccination_form.html', context)


# ============== Medical Documents ==============

@login_required
def document_list(request):
    """List all medical documents for the current patient"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    documents = patient.medical_documents.all()

    # Filter by document type if requested
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)

    context = {
        'documents': documents,
        'patient': patient,
    }
    return render(request, 'medical_records/document_list.html', context)


@login_required
def upload_document(request):
    """Upload a new medical document"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    if request.method == 'POST':
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.uploaded_by = request.user
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect('medical_records:document_list')
    else:
        form = MedicalDocumentForm()

    context = {'form': form, 'patient': patient}
    return render(request, 'medical_records/document_form.html', context)


@login_required
def view_document(request, document_id):
    """View document details"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')

    document = get_object_or_404(MedicalDocument, document_id=document_id, patient=patient)

    context = {'document': document, 'patient': patient}
    return render(request, 'medical_records/document_detail.html', context)


@login_required
def download_document(request, document_id):
    """Download a medical document"""
    try:
        patient = request.user.patient_info
    except Patient.DoesNotExist:
        raise Http404("Patient profile not found")

    document = get_object_or_404(MedicalDocument, document_id=document_id, patient=patient)

    if not document.file:
        raise Http404("File not found")

    response = FileResponse(document.file.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{document.file.name.split("/")[-1]}"'
    return response


# ============== Medical Summary ==============

@login_required
def medical_summary(request, patient_id):
    """Comprehensive medical summary for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)

    # Check permission - user must be the patient or a doctor
    if request.user != patient.user:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'doctor':
            messages.error(request, "You don't have permission to view this patient's records.")
            return redirect('dashboards:patient_dashboard')

    # Get all medical data
    conditions = patient.medical_conditions.filter(status__in=['active', 'chronic'])
    allergies = patient.allergies.filter(is_active=True)
    medications = patient.medications.filter(status='current')
    vaccinations = patient.vaccinations.all()[:5]  # Latest 5
    recent_documents = patient.medical_documents.all()[:5]
    latest_risk_score = patient.risk_scores.first()

    # Get lifestyle info
    try:
        lifestyle = patient.lifestyle_info
    except LifestyleInformation.DoesNotExist:
        lifestyle = None

    context = {
        'patient': patient,
        'conditions': conditions,
        'allergies': allergies,
        'medications': medications,
        'vaccinations': vaccinations,
        'recent_documents': recent_documents,
        'lifestyle': lifestyle,
        'latest_risk_score': latest_risk_score,
    }
    return render(request, 'medical_records/medical_summary.html', context)


# ============== Risk Assessment ==============

@login_required
def calculate_risk_score(request, patient_id):
    """Calculate COVID-19 risk score for a patient"""
    patient = get_object_or_404(Patient, id=patient_id)

    # Check permission
    if request.user != patient.user:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'doctor':
            messages.error(request, "You don't have permission to calculate risk score for this patient.")
            return redirect('dashboards:patient_dashboard')

    # Calculate risk score
    risk_score = RiskAssessmentService.calculate_risk_score(patient, request.user)

    messages.success(request, f"Risk assessment completed. Risk Level: {risk_score.get_risk_level_display()}")

    return render(request, 'medical_records/risk_assessment.html', {
        'patient': patient,
        'risk_score': risk_score,
    })


@login_required
def medical_summary_current_user(request):
    """Redirect to medical summary for the current logged-in user"""
    try:
        patient = request.user.patient_info
        return medical_summary(request, patient.id)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('dashboards:patient_dashboard')
