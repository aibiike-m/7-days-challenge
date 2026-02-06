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

REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
    "anon": None,
    "user": None,
    "login": None,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# CSRF
MIDDLEWARE = [m for m in MIDDLEWARE if "CsrfViewMiddleware" not in m]
