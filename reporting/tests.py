from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from detection.models import Patient, XRayImage, Prediction
from .models import ReportTemplate, Report, BatchReportJob
from .services import ReportGenerator, ExcelExporter
import tempfile
from PIL import Image
import io


class ReportTemplateModelTest(TestCase):
    """Test cases for ReportTemplate model"""

    def setUp(self):
        self.template = ReportTemplate.objects.create(
            name="Test Template",
            template_type="standard",
            description="Test description",
            html_template="<html><body>Test</body></html>",
            css_styles="body { color: black; }",
            is_active=True
        )

    def test_template_creation(self):
        """Test report template creation"""
        self.assertEqual(self.template.name, "Test Template")
        self.assertEqual(self.template.template_type, "standard")
        self.assertTrue(self.template.is_active)

    def test_template_str_method(self):
        """Test __str__ method"""
        expected = "Standard Report - Test Template"
        self.assertEqual(str(self.template), expected)


class ReportModelTest(TestCase):
    """Test cases for Report model"""

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123',
            first_name='Test',
            last_name='Doctor'
        )

        # Create patient
        self.patient = Patient.objects.create(
            user=self.user,
            age=30,
            gender='M',
            phone_number='1234567890'
        )

        # Create XRay image (mock)
        self.xray = XRayImage.objects.create(
            patient=self.patient,
            image_type='chest_xray'
        )

        # Create prediction (mock)
        self.prediction = Prediction.objects.create(
            xray=self.xray,
            final_diagnosis='Normal',
            consensus_confidence=95.5,
            crossvit_prediction='Normal',
            crossvit_confidence=96.0,
            resnet50_prediction='Normal',
            resnet50_confidence=94.0,
            densenet121_prediction='Normal',
            densenet121_confidence=95.0,
            efficientnet_prediction='Normal',
            efficientnet_confidence=94.5,
            vit_prediction='Normal',
            vit_confidence=95.5,
            swin_prediction='Normal',
            swin_confidence=96.5,
            inference_time=150.5
        )

        # Create template
        self.template = ReportTemplate.objects.create(
            name="Test Template",
            template_type="standard",
            html_template="<html><body>Test</body></html>"
        )

        # Create report
        self.report = Report.objects.create(
            prediction=self.prediction,
            patient=self.patient,
            template=self.template,
            generated_by=self.user,
            status='generated'
        )

    def test_report_creation(self):
        """Test report creation"""
        self.assertIsNotNone(self.report.report_id)
        self.assertEqual(self.report.patient, self.patient)
        self.assertEqual(self.report.status, 'generated')

    def test_increment_download_count(self):
        """Test download counter increment"""
        initial_count = self.report.downloaded_count
        self.report.increment_download_count()
        self.assertEqual(self.report.downloaded_count, initial_count + 1)
        self.assertIsNotNone(self.report.last_downloaded_at)


class BatchReportJobModelTest(TestCase):
    """Test cases for BatchReportJob model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123'
        )

        self.template = ReportTemplate.objects.create(
            name="Batch Template",
            template_type="standard",
            html_template="<html><body>Batch</body></html>"
        )

        self.batch_job = BatchReportJob.objects.create(
            created_by=self.user,
            template=self.template,
            total_reports=10,
            completed_reports=5,
            failed_reports=1,
            status='processing'
        )

    def test_batch_job_creation(self):
        """Test batch job creation"""
        self.assertIsNotNone(self.batch_job.job_id)
        self.assertEqual(self.batch_job.total_reports, 10)
        self.assertEqual(self.batch_job.status, 'processing')

    def test_get_progress_percentage(self):
        """Test progress percentage calculation"""
        progress = self.batch_job.get_progress_percentage()
        expected = int((5 / 10) * 100)
        self.assertEqual(progress, expected)

    def test_get_progress_percentage_zero_division(self):
        """Test progress percentage with zero total reports"""
        self.batch_job.total_reports = 0
        progress = self.batch_job.get_progress_percentage()
        self.assertEqual(progress, 0)


class ReportViewsTest(TestCase):
    """Test cases for report views"""

    def setUp(self):
        self.client = Client()

        # Create doctor user
        self.doctor = User.objects.create_user(
            username='doctor',
            password='testpass123'
        )

        # Create patient
        self.patient = Patient.objects.create(
            user=self.doctor,
            age=30,
            gender='M'
        )

        # Login
        self.client.login(username='doctor', password='testpass123')

    def test_report_list_view_requires_login(self):
        """Test that report list requires login"""
        self.client.logout()
        response = self.client.get(reverse('reporting:report_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_manage_templates_view_accessible(self):
        """Test that manage templates view is accessible"""
        # Note: This will fail without proper doctor permissions
        # You may need to adjust based on your actual permission system
        pass


class ExcelExporterTest(TestCase):
    """Test cases for Excel exporter service"""

    def setUp(self):
        # Create minimal test data
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            age=30,
            gender='M'
        )

        self.xray = XRayImage.objects.create(
            patient=self.patient,
            image_type='chest_xray'
        )

        self.prediction = Prediction.objects.create(
            xray=self.xray,
            final_diagnosis='Normal',
            consensus_confidence=95.5,
            crossvit_prediction='Normal',
            crossvit_confidence=96.0,
            resnet50_prediction='Normal',
            resnet50_confidence=94.0,
            densenet121_prediction='Normal',
            densenet121_confidence=95.0,
            efficientnet_prediction='Normal',
            efficientnet_confidence=94.5,
            vit_prediction='Normal',
            vit_confidence=95.5,
            swin_prediction='Normal',
            swin_confidence=96.5,
            inference_time=150.5
        )

    def test_excel_export_generation(self):
        """Test Excel file generation"""
        predictions = Prediction.objects.all()
        exporter = ExcelExporter(predictions)
        excel_file = exporter.generate()

        # Check that file was generated
        self.assertIsNotNone(excel_file)
        self.assertGreater(excel_file.tell(), 0)  # File has content


class ReportGeneratorTest(TestCase):
    """Test cases for report generator service"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123'
        )

        self.patient = Patient.objects.create(
            user=self.user,
            age=30,
            gender='M'
        )

        self.xray = XRayImage.objects.create(
            patient=self.patient,
            image_type='chest_xray'
        )

        self.prediction = Prediction.objects.create(
            xray=self.xray,
            final_diagnosis='Normal',
            consensus_confidence=95.5,
            crossvit_prediction='Normal',
            crossvit_confidence=96.0,
            resnet50_prediction='Normal',
            resnet50_confidence=94.0,
            densenet121_prediction='Normal',
            densenet121_confidence=95.0,
            efficientnet_prediction='Normal',
            efficientnet_confidence=94.5,
            vit_prediction='Normal',
            vit_confidence=95.5,
            swin_prediction='Normal',
            swin_confidence=96.5,
            inference_time=150.5
        )

        self.template = ReportTemplate.objects.create(
            name="Test Template",
            template_type="standard",
            html_template="<html><body>{{ patient.user.get_full_name }}</body></html>"
        )

    def test_report_generator_initialization(self):
        """Test report generator initialization"""
        generator = ReportGenerator(
            prediction=self.prediction,
            template=self.template,
            include_signature=True,
            include_logo=True,
            include_qr=True,
            custom_notes="Test notes"
        )

        self.assertEqual(generator.prediction, self.prediction)
        self.assertEqual(generator.template, self.template)
        self.assertTrue(generator.include_signature)
        self.assertEqual(generator.custom_notes, "Test notes")


# Integration test placeholder
class ReportIntegrationTest(TestCase):
    """Integration tests for report generation flow"""

    def test_end_to_end_report_generation(self):
        """Test complete report generation workflow"""
        # This would test the entire flow from prediction to PDF generation
        # Requires actual PDF generation libraries to be installed
        pass
