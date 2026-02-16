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
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": None,
        "user": None,
        "login": None,
        "email_change": None,
    },
}

# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
