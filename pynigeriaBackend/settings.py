from pathlib import Path
from dotenv import load_dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    print("No env file detected.")
    exit(code=5000)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY_VALUE", default="default")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG_VALUE", "true").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS_VALUE", "127.0.0.1").split(",") # Use commas to seperate muliple host values
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS_VALUE", "http://127.0.0.1").split(",") # Same comma-value-seperation as above

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-Party packages
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular", # for openapi/swagger documentation
    "drf_spectacular_sidecar",
    "django_otp", # for 2FA
    "django_otp.plugins.otp_totp",
    "django_filters",
    "authentication.apps.AuthenticationConfig",
    "job_application_api.apps.JobApplicationApiConfig",
    "job_listing_api.apps.JobApiConfig",
    "job.apps.JobConfig",
    "knowledge_base_api.apps.KnowledgeBaseApiConfig",
    "tracking",
    # For social auth
    "oauth2_provider",
    "social_django",
    "drf_social_oauth2",
    "taggit",
]

MIDDLEWARE = [
   "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware", # 2FA middleware
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pynigeriaBackend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pynigeriaBackend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTH_USER_MODEL = "authentication.User"

REST_FRAMEWORK = {
    "REST_FRAMEWORK_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "15/min",
        "user": "30/min",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "pynigeriaBackend.exception_handler.pynigeria_exception_handler",

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "PYNIGERIA BACKEND API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

# Email settings
CURRENT_ORIGIN = os.getenv("CURRENT_ORIGIN_VALUE")
SENDER_EMAIL = os.getenv("SENDER_EMAIL_VALUE")
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND_VALUE")
EMAIL_HOST = os.getenv("EMAIL_HOST_VALUE")
EMAIL_PORT = os.getenv("EMAIL_PORT_VALUE")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER_VALUE")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD_VALUE")

# 2FA TOTP settings
OTP_TOTP_ISSUER = "pynigeria"