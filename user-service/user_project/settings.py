from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-please-change")

DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true")


raw_hosts = os.getenv("ALLOWED_HOSTS", "") 

if raw_hosts == "*": 
    ALLOWED_HOSTS = ["*"] 
else: 
    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]


PUBLIC_KEY_PATH = "/app/keys/public.pem"


if os.path.exists(PUBLIC_KEY_PATH): 
    with open(PUBLIC_KEY_PATH, "r") as f: 
        JWT_PUBLIC_KEY = f.read() 
else: JWT_PUBLIC_KEY = None 


AUTH_PUBLIC_KEY = JWT_PUBLIC_KEY 


AUTH_USER_MODEL = "user_app.User"





INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",

    'user_app.apps.UserAppConfig',
    "corsheaders",
    "user_app",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'user_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'user_project.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {"NAME": 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {"NAME": 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {"NAME": 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = { 
    "DEFAULT_AUTHENTICATION_CLASSES": [ 
        "user_app.remote_auth.RemoteJWTAuthentication", 
        "rest_framework.authentication.SessionAuthentication", 
    ] 
}


SIMPLE_JWT = { 
    "ALGORITHM": "RS256", 
    "VERIFYING_KEY": JWT_PUBLIC_KEY, 
    "AUTH_HEADER_TYPES": ("Bearer",), 
}


EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_MIN_SCORE = float(os.getenv("RECAPTCHA_MIN_SCORE", 0.5))

SOCIAL_AUTH = {
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
    "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI"),
    "MICROSOFT_CLIENT_ID": os.getenv("MICROSOFT_CLIENT_ID"),
    "MICROSOFT_CLIENT_SECRET": os.getenv("MICROSOFT_CLIENT_SECRET"),
    "MICROSOFT_TENANT_ID": os.getenv("MICROSOFT_TENANT_ID"),
    "MICROSOFT_REDIRECT_URI": os.getenv("MICROSOFT_REDIRECT_URI"),
}

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
USER_SERVICE_INTERNAL_TOKEN = os.getenv("USER_SERVICE_INTERNAL_TOKEN")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
