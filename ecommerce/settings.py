"""
Django settings for ecommerce project.
"""

import os
from pathlib import Path
import dj_database_url
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG") == "True"

# Vercel deployment detection
IS_VERCEL = os.getenv("VERCEL") == "1"

# Allowed hosts configuration
if IS_VERCEL:
    ALLOWED_HOSTS = ['.vercel.app', '.now.sh', 'localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",
    "drf_spectacular",
    "django_filters",

    # Local apps
    "users",
    "categories",
    "products",
    "addresses",
    "coupons",
    "cart",
    "whitenoise.runserver_nostatic",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# Enforce a single Postgres URL (e.g., Supabase) with no SQLite fallback
from dj_database_url import ParseError as _DJParseError


def _clean_database_url(raw: str) -> str:
    if raw is None:
        return ""
    # Trim whitespace and newlines
    cleaned = raw.strip().replace("\n", "").replace("\r", "").strip()
    # Remove a single pair of wrapping quotes if present
    if cleaned and cleaned[0] == cleaned[-1] and cleaned[0] in ("'", '"'):
        cleaned = cleaned[1:-1].strip()
    return cleaned


DATABASE_URL_ENV = _clean_database_url(os.getenv("DATABASE_URL"))

if not DATABASE_URL_ENV:
    raise RuntimeError(
        "DATABASE_URL not configured. Set a single Postgres URL (e.g., Supabase) without quotes."
    )

try:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL_ENV,
            conn_max_age=600,
            ssl_require=IS_VERCEL,
        )
    }
except _DJParseError as exc:
    raise RuntimeError(
        "Invalid DATABASE_URL. Provide a valid Postgres URL (e.g., Supabase pooling URL) "
        "without surrounding quotes or whitespace, e.g. postgresql://user:pass@host:6543/db?sslmode=require"
    ) from exc

# Cache Configuration with Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'ecommerce',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Use Redis for session storage (optional but recommended for production)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Cache time to live is 15 minutes (in seconds)
CACHE_TTL = 60 * 15

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

AUTH_USER_MODEL = "users.User"

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Ecommerce API",
    "DESCRIPTION": "API for E-commerce Backend (Project Nexus)",
    "VERSION": "1.0.0",
}
