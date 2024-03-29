"""
Django settings for weplate project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import environ
import os

from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
from urllib.parse import urlparse

from google.oauth2 import service_account

BASE_DIR = Path(__file__).resolve().parent.parent

SETTINGS_LOG_MSG = []

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-h1#o@85ph_lx=$*pcdfo$=w^m_ayh6tl($9&ceftmzncu+d5fp'),
    PROD=(bool, False),
    GS_BUCKET_NAME=(str, '')
)
env_file = os.environ.get('ENV_FILE', '.env')
SETTINGS_LOG_MSG.append(('.env file', env_file))
environ.Env.read_env(BASE_DIR / env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
PROD = env('PROD')

ALLOWED_HOSTS = ['*']  # Bro...
SECURE_REDIRECT_EXEMPT = [r'^jobs/.*']  # Don't redirect any appengine jobs to https

# Application definition
INSTALLED_APPS = [
    'backend.apps.BackendConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'debug_permissions',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'weplate.urls'

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

WSGI_APPLICATION = 'weplate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': env.db()
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'weplate_cache_table',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'backend.utils.IsStudent',
        'backend.utils.IsVerified'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
STATIC_ROOT = 'static_weplate'
STATIC_URL = '/static_weplate/'
# TODO: consider moving static file storage to gcloud too?
# https://django-storages.readthedocs.io/en/latest/backends/gcloud.html

# GS file storage
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_BUCKET_NAME = env('GS_BUCKET_NAME')
GS_PROJECT_ID = 'weplate-backend'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    'gae-service-account-key.json'
)

# Email sending
SENDGRID_EMAIL_SENDER = 'info@weplate.app'
SENDGRID_API_KEY = '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'

# Job related things
JOB_LOG_MAX_SIZE = 1000

# Versioning
BACKEND_VERSION = '1.0.0'
MAINTENANCE = True
