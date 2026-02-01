from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Rate limiting for login endpoint.
    """

    scope = "login"
