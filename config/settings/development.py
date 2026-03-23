from .base import *

CSRF_COOKIE_SAMESITE = 'None'
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000',"https://pynigeria.vercel.app/"]
CSRF_COOKIE_HTTPONLY = False
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition


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



STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



CURRENT_ORIGIN = "https://pynigeria.vercel.app/"


# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # your frontend URL
]

# Allow cookies/credentials to be sent
CORS_ALLOW_CREDENTIALS = True

CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

