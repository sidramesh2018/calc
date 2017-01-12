from rest_framework import permissions
from django.conf import settings


class WhiteListPermission(permissions.BasePermission):
    """
    This class is used in our Django Rest Framework to check
    that the incoming request is from a whitelisted IP.

    In practice, it is used to only allow requests to our backend API
    to come directly from an api.data.gov proxy.
    """

    def has_permission(self, request, view):
        if not settings.REST_FRAMEWORK['WHITELIST']:
            # if no WHITELIST, then permission is allowed
            return True

        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            ip_addresses = [f.strip() for f in forwarded.split(',')]
        else:
            ip_addresses = [request.META['REMOTE_ADDR']]

        for ip in ip_addresses:
            if ip in settings.REST_FRAMEWORK['WHITELIST']:
                return True

        return False
