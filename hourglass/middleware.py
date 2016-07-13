from django.conf import settings


class ComplianceMiddleware:
    '''
    Middleware to add security-related response headers.

    If the SECURITY_HEADERS_ON_ERROR_ONLY setting is True, then the headers
    will only be added to error responses (400 and above). This behavior is
    needed for cloud.gov deployments because its proxy adds the headers
    to 200 responses, but not to error responses.

    Otherwise, the headers will be added to all responses.
    '''
    def process_response(self, request, response):
        if (not settings.SECURITY_HEADERS_ON_ERROR_ONLY or
           response.status_code >= 400):

            response["X-Content-Type-Options"] = "nosniff"
            response["X-XSS-Protection"] = "1; mode=block"

        return response
