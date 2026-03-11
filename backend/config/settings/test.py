from config.settings.base import *

# Security
DEBUG = True
SECRET_KEY = "test-secret-key-for-testing-only-not-production"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Password hashing
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Email
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

# Caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Throttling
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": None,
        "user": None,
        "login": None,
        "email_change": None,
        "password_reset": None,
        "verification_code": None,
    },
}

# Axes
AXES_ENABLED = False

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# CSRF
MIDDLEWARE = [m for m in MIDDLEWARE if "CsrfViewMiddleware" not in m]
MIDDLEWARE = [m for m in MIDDLEWARE if "AxesMiddleware" not in m]
