from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log certain requests
    """
    def process_request(self, request):
        # Store request start time for performance tracking
        import time
        request._audit_start_time = time.time()

    def process_response(self, request, response):
        # Log certain actions automatically
        if request.user.is_authenticated:
            # Log file downloads
            if 'download' in request.path and response.status_code == 200:
                AuditLog.log(
                    user=request.user,
                    action_type='download',
                    description=f"Downloaded file: {request.path}",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='info'
                )

        return response

    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
