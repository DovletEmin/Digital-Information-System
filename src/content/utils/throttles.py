"""
Custom throttling classes for API rate limiting.
Implements different throttling strategies for different endpoints.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class SearchRateThrottle(UserRateThrottle):
    """Throttle for search endpoints - more restrictive"""

    scope = "search"


class AuthRateThrottle(AnonRateThrottle):
    """Throttle for authentication endpoints - very restrictive"""

    scope = "auth"


class BurstRateThrottle(UserRateThrottle):
    """Allow burst of requests but limit sustained load"""

    scope = "burst"
    rate = "60/minute"
