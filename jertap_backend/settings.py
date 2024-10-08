"""
Django settings for jertap_backend project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path
from decouple import config
import dj_database_url
from kombu.utils.url import safequote

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r3m)$k=-sgjkt!@-rms2qb7zky-ff6+=cgx90btluaf652=v+o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION')

ALLOWED_HOSTS = ['*', ]

ENABLE_API_DOCS = config('ENABLE_API_DOCS', cast=bool)
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.gis',
    'corsheaders',
    'rest_framework',
    "rest_auth",
    'django_filters',
    'storages',
    'django_cleanup.apps.CleanupConfig',

    'users',
    'core',
    'owner_dashboard',
    'admin_dashboard',
    'social',

]

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware'
]

CSRF_TRUSTED_ORIGINS = [
    'http://*.127.0.0.1:8000',
    'https://*.ngrok-free.app',
    'https://*.ap-south-1.compute.amazonaws.com',
    'http://*.ap-south-1.compute.amazonaws.com',
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'jertap_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'jertap_backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(config('DEFAULT_DATABASES'))
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "users.User"
# Config to make the registration email only
ACCOUNT_USER_MODEL_USERNAME_FIELD = "email"
ACCOUNT_USERNAME_REQUIRED = False
# OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    # "DATE_INPUT_FORMATS": ["%d/%m/%Y", "%Y-%m-%d"],
    # "DATETIME_INPUT_FORMATS": ["%Y-%m-%dT%H:%M:%S.%fZ", ],

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',

    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/day',
    },

}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

if config('USE_S3', cast=bool):
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")
    # AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_CUSTOM_DOMAIN = "%s.s3.ap-south-1.amazonaws.com" % (AWS_STORAGE_BUCKET_NAME)

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',)
    STATICFILES_LOCATION = 'static'
    STATICFILES_STORAGE = 'custom_storages.StaticStorage'
    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)

    MEDIAFILES_LOCATION = 'media'
    MEDIA_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
# for local
else:
    MEDIA_URL = 'media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
    STATIC_URL = '/static/'
    static_root = os.path.join(BASE_DIR, "static/")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

PASS_REST_CONFIRM_EXPIRE_MINUTE = 5
VERIFICATION_CODE_EXPIRE_MINUTE = 5

GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
SOCIAL_SECRET = config('SOCIAL_SECRET')

# celery Configuration

# Celery for AWS
if config('USE_SQS', cast=bool):
    sqs_host_endpoint = config('SQS_HOST_ENDPOINT')
    aws_access_key_id = safequote(AWS_ACCESS_KEY_ID)
    aws_secret_access_key = safequote(AWS_SECRET_ACCESS_KEY)
    CELERY_BROKER_URL = f"sqs://{aws_access_key_id}:{aws_secret_access_key}@{sqs_host_endpoint}"

# Celery for Local
else:
    CELERY_BROKER_URL = 'pyamqp://guest@localhost//'

# celery -A jertap_backend worker -l info

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Email configuration
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = config('AWS_SES_REGION_NAME')
SES_SENDER_EMAIL = config('SES_SENDER_EMAIL')
SEND_EMAIL = config('SEND_EMAIL', cast=bool)
SEND_SMS = config('SEND_SMS', cast=bool)

# SMS configuration
SMSC_LOGIN = config('SMSC_LOGIN')
SMSC_PASSWORD = config('SMSC_PASSWORD')