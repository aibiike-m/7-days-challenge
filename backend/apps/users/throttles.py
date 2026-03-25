from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.utils import timezone


class LoginRateThrottle(UserRateThrottle):
    scope = "login"


class EmailChangeRateThrottle(UserRateThrottle):
    scope = "email_change"


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = "password_reset"


class VerificationCodeRateThrottle(UserRateThrottle):
    scope = "verification_code"


class MinimumIntervalThrottle(AnonRateThrottle):

    def __init__(self):
        self.minimum_interval_seconds = getattr(
            self, "minimum_interval_seconds", 60
        )

    def allow_request(self, request, view):
        if request.user.is_authenticated:
            ident = f"user_{request.user.id}"
        else:
            ident = self.get_ident(request)

        cache_key = f"throttle_interval_{self.__class__.__name__}_{ident}"

        last_request_time = cache.get(cache_key)

        now = timezone.now()

        if last_request_time:
            time_passed = (now - last_request_time).total_seconds()

            if time_passed < self.minimum_interval_seconds:
                self.wait_seconds = self.minimum_interval_seconds - time_passed
                return False

        cache.set(
            cache_key,
            now,
            timeout=self.minimum_interval_seconds + 10,
        )

        return True

    def wait(self):
        return getattr(self, "wait_seconds", self.minimum_interval_seconds)

    def get_ident(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        remote_addr = request.META.get("REMOTE_ADDR")

        if xff:
            return xff.split(",")[0].strip()

        return remote_addr


class CodeSendingThrottle(MinimumIntervalThrottle):
    minimum_interval_seconds = 60


class ChallengeCreationThrottle(UserRateThrottle):
    scope = "challenge_creation"


class PasswordChangeRateThrottle(UserRateThrottle):
    scope = "password_change"


class GoogleAuthThrottle(AnonRateThrottle):
    scope = "google_auth"


class TokenActionThrottle(AnonRateThrottle):
    scope = "token_action"
