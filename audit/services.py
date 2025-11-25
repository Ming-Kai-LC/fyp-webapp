from django.utils import timezone
from django.db.models import Count, Q
from .models import (
    AuditLog, DataAccessLog, LoginAttempt, ComplianceReport, SecurityAlert
)
from detection.models import Prediction, Patient
from io import BytesIO, StringIO
import csv


class ComplianceReportGenerator:
    """
    Generate compliance reports for regulatory review
    """
    def __init__(self, report_type, start_date, end_date):
        self.report_type = report_type
        self.start_date = start_date
        self.end_date = end_date

    def generate(self, generated_by):
        """
        Generate compliance report based on type
        """
        if self.report_type == 'hipaa_audit':
            summary, details = self._generate_hipaa_audit()
        elif self.report_type == 'gdpr_compliance':
            summary, details = self._generate_gdpr_compliance()
        elif self.report_type == 'access_review':
            summary, details = self._generate_access_review()
        elif self.report_type == 'security_audit':
            summary, details = self._generate_security_audit()
        elif self.report_type == 'user_activity':
            summary, details = self._generate_user_activity()
        else:
            summary, details = {}, {}

        # Create report
        report = ComplianceReport.objects.create(
            report_type=self.report_type,
            generated_by=generated_by,
            start_date=self.start_date,
            end_date=self.end_date,
            summary=summary,
            details=details
        )

        return report

    def _generate_hipaa_audit(self):
        """
        Generate HIPAA compliance audit report
        """
        # Patient data access logs
        access_logs = DataAccessLog.objects.filter(
            accessed_at__range=[self.start_date, self.end_date]
        )

        # Summary statistics
        summary = {
            'total_access_events': access_logs.count(),
            'unique_patients_accessed': access_logs.values('patient').distinct().count(),
            'unique_accessors': access_logs.values('accessor').distinct().count(),
            'flagged_accesses': access_logs.filter(flagged_for_review=True).count(),
            'access_by_type': dict(access_logs.values('access_type').annotate(count=Count('id')).values_list('access_type', 'count')),
        }

        # Detailed findings
        details = {
            'flagged_accesses': list(
                access_logs.filter(flagged_for_review=True).values(
                    'accessor__username',
                    'patient__user__username',
                    'data_type',
                    'accessed_at',
                    'access_reason'
                )
            ),
            'high_volume_accessors': list(
                access_logs.values('accessor__username').annotate(
                    count=Count('id')
                ).filter(count__gte=50).order_by('-count')
            ),
        }

        return summary, details

    def _generate_gdpr_compliance(self):
        """
        Generate GDPR compliance report
        """
        audit_logs = AuditLog.objects.filter(
            created_at__range=[self.start_date, self.end_date]
        )

        summary = {
            'data_access_requests': audit_logs.filter(action_type='read').count(),
            'data_exports': audit_logs.filter(action_type='export').count(),
            'data_deletions': audit_logs.filter(action_type='delete').count(),
            'consent_changes': 0,  # Implement when consent module is added
        }

        details = {
            'export_requests': list(
                audit_logs.filter(action_type='export').values(
                    'username', 'action_description', 'created_at'
                )
            ),
            'deletion_requests': list(
                audit_logs.filter(action_type='delete').values(
                    'username', 'action_description', 'created_at'
                )
            ),
        }

        return summary, details

    def _generate_access_review(self):
        """
        Generate data access review report
        """
        access_logs = DataAccessLog.objects.filter(
            accessed_at__range=[self.start_date, self.end_date]
        )

        summary = {
            'total_accesses': access_logs.count(),
            'by_role': dict(access_logs.values('accessor_role').annotate(count=Count('id')).values_list('accessor_role', 'count')),
            'by_data_type': dict(access_logs.values('data_type').annotate(count=Count('id')).values_list('data_type', 'count')),
        }

        details = {
            'top_accessors': list(
                access_logs.values('accessor__username', 'accessor_role').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
            'most_accessed_patients': list(
                access_logs.values('patient__user__username').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
        }

        return summary, details

    def _generate_security_audit(self):
        """
        Generate security audit report
        """
        login_attempts = LoginAttempt.objects.filter(
            created_at__range=[self.start_date, self.end_date]
        )

        security_alerts = SecurityAlert.objects.filter(
            triggered_at__range=[self.start_date, self.end_date]
        )

        summary = {
            'total_login_attempts': login_attempts.count(),
            'failed_logins': login_attempts.filter(success=False).count(),
            'suspicious_logins': login_attempts.filter(is_suspicious=True).count(),
            'security_alerts': security_alerts.count(),
            'critical_alerts': security_alerts.filter(severity='critical').count(),
        }

        details = {
            'failed_login_trends': list(
                login_attempts.filter(success=False).values('username').annotate(
                    count=Count('id')
                ).order_by('-count')[:10]
            ),
            'alert_breakdown': list(
                security_alerts.values('alert_type', 'severity').annotate(
                    count=Count('id')
                ).order_by('-count')
            ),
        }

        return summary, details

    def _generate_user_activity(self):
        """
        Generate user activity report
        """
        audit_logs = AuditLog.objects.filter(
            created_at__range=[self.start_date, self.end_date]
        )

        summary = {
            'total_actions': audit_logs.count(),
            'unique_users': audit_logs.values('user').distinct().count(),
            'by_action_type': dict(audit_logs.values('action_type').annotate(count=Count('id')).values_list('action_type', 'count')),
        }

        details = {
            'most_active_users': list(
                audit_logs.values('username').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
            'action_timeline': list(
                audit_logs.values('created_at__date', 'action_type').annotate(
                    count=Count('id')
                ).order_by('created_at__date')
            ),
        }

        return summary, details


class AuditExporter:
    """
    Export audit logs to CSV
    """
    def __init__(self, date_from=None, date_to=None, action_type=None):
        self.date_from = date_from
        self.date_to = date_to
        self.action_type = action_type

    def export_to_csv(self):
        """
        Export filtered audit logs to CSV
        """
        logs = AuditLog.objects.all()

        if self.date_from:
            logs = logs.filter(created_at__gte=self.date_from)
        if self.date_to:
            logs = logs.filter(created_at__lte=self.date_to)
        if self.action_type:
            logs = logs.filter(action_type=self.action_type)

        # Create CSV
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        # Headers
        writer.writerow([
            'Timestamp', 'Username', 'Action Type', 'Description',
            'Severity', 'IP Address', 'Success', 'Error Message'
        ])

        # Data
        for log in logs:
            writer.writerow([
                log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                log.username,
                log.action_type,
                log.action_description,
                log.severity,
                log.ip_address or 'N/A',
                'Yes' if log.success else 'No',
                log.error_message or 'N/A'
            ])

        csv_buffer.seek(0)
        return csv_buffer


class SecurityMonitor:
    """
    Monitor for suspicious activities and trigger alerts
    """
    @staticmethod
    def check_failed_login_attempts(username, ip_address):
        """
        Check for multiple failed login attempts
        """
        from datetime import timedelta

        # Check last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        failed_attempts = LoginAttempt.objects.filter(
            username=username,
            success=False,
            created_at__gte=one_hour_ago
        ).count()

        if failed_attempts >= 5:
            SecurityAlert.objects.create(
                alert_type='failed_login',
                severity='high',
                description=f"Multiple failed login attempts for user {username} from IP {ip_address}",
                ip_address=ip_address,
                auto_blocked=True,
                admin_notified=True
            )
            return True

        return False

    @staticmethod
    def check_unusual_access_pattern(accessor, patient):
        """
        Detect unusual data access patterns
        """
        # Check if accessor has accessed this patient before
        previous_accesses = DataAccessLog.objects.filter(
            accessor=accessor,
            patient=patient
        ).count()

        # Check if accessing many different patients in short time
        from datetime import timedelta
        last_hour = timezone.now() - timedelta(hours=1)
        recent_unique_patients = DataAccessLog.objects.filter(
            accessor=accessor,
            accessed_at__gte=last_hour
        ).values('patient').distinct().count()

        if recent_unique_patients >= 20:  # Accessing 20+ patients in 1 hour
            SecurityAlert.objects.create(
                alert_type='unusual_access',
                severity='medium',
                description=f"User {accessor.username} accessed {recent_unique_patients} different patient records in the last hour",
                user=accessor,
                admin_notified=True
            )
