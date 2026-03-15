from config.settings.base import *

# Security
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Static files
STATICFILES_DIRS = (BASE_DIR / "static",)

# REST Framework
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/hour",
        "user": "10000/hour",
        "login": "3/minute",
        "email_change": "2/minute",
        "password_change": "2/minute",
        "password_reset": "2/minute",
        "verification_code": "2/minute",
        "challenge_creation": "5/minute",
        "google_auth": "10/minute",
        "token_action": "20/minute",
    },
}

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = f"SevenSteps <{env('EMAIL_HOST_USER')}>"

# CACHES
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "axes": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "axes-cache",
    },
}

AXES_CACHE = "axes"

# 🔒 Axes
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = timedelta(minutes=3)


MAX_ACTIVE_CHALLENGES = 3
MAX_CHALLENGES_PER_DAY = 5
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["challenge_creation"] = "3/hour"
