from datetime import timedelta
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# Security
SECRET_KEY = env("SECRET_KEY")

# Application definition
INSTALLED_APPS = [
    "anymail",
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "djoser",
    "corsheaders",
    "axes",
    "apps.challenges",
    "apps.users",
    "drf_spectacular",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
]

# Static files
STATIC_URL = "/static/"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.CustomUser"

# Social Auth - Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("GOOGLE_OAUTH2_KEY", default="")

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/minute",
        "user": "1000/day",
        "login": "5/minute",
        "email_change": "5/hour",
        "password_reset": "5/hour",
        "verification_code": "5/minute",
        "code_sending": "5/minute",
        "challenge_creation": "10/hour",
        "google_auth": "10/minute",
        "token_action": "20/minute",
        "password_change": "5/hour",
    },
}

# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
}

# Djoser
DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SERIALIZERS": {
        "user_create": "apps.users.serializers.RegisterSerializer",
        "user": "apps.users.serializers.UserSerializer",
        "current_user": "apps.users.serializers.UserSerializer",
    },
}

AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = [["username"]]
AXES_LOCKOUT_TEMPLATE = None
AXES_VERBOSE = True
AXES_USERNAME_FORM_FIELD = "email"
AXES_LOCK_OUT_AT_FAILURE = True

# CACHES (Axes and throttles)
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

# Email Configuration
EMAIL_TIMEOUT = 10

FRONTEND_URL = env("FRONTEND_URL")


# Challenge limits
MAX_CHALLENGES_PER_DAY = 15
MAX_ACTIVE_CHALLENGES = 10

# Browser security headers
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

# Spectacular Settings
SPECTACULAR_SETTINGS = {
    "TITLE": "SevenSteps API",
    "DESCRIPTION": "AI-powered goal achievement app",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_PATCH": True,
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [
        {"Bearer": []},
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}
