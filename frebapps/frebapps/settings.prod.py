"""
Django settings for frebapps project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

with open('/etc/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['geosnapr.com']

USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

INSTAGRAM_APP_ID = '643e9ed337374c15b605d64d86b7acde'

with open('/etc/instagram_secret.txt') as f:
    INSTAGRAM_APP_SECRET = f.read().strip()

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'geosnapr',
    'storages',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'frebapps.urls'

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

WSGI_APPLICATION = 'frebapps.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

with open('/etc/db_pass.txt') as f:
    DB_PASS = f.read().strip()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'geosnapr',
        'USER': 'admin',
        'PASSWORD': DB_PASS,
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/django/geosnapr.log'
        },
    },
    'loggers': {
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Default album name
DEFAULT_ALBUM_NAME = "All Images"

# Default public album name
DEFAULT_PUBLIC_NAME = "My Public Images"

# Server hostname
HOSTNAME = 'geosnapr.com'

# HTTP scheme
SCHEME = 'https'

# Acceptable image content types
CONTENT_TYPES = ['image']

# Maximum allowable file size -> 5MB
MAX_UPLOAD_SIZE = 5242880

# Maximum images that a user can own
MAX_PHOTOS = 200

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

#STATIC_URL = '/static/'

#MEDIA_URL = '/media/'

#MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

LOGIN_URL = ''

LOGIN_REDIRECT_URL = ''

LOGOUT_URL = '/logout/'

# AWS S3 STORAGE INFO

AWS_STORAGE_BUCKET_NAME = 'geosnapr'

AWS_ACCESS_KEY_ID = 'AKIAJ7VBAHLVGLYCLLWA'

with open('/etc/aws_secret_key.txt') as f:
    AWS_SECRET_ACCESS_KEY = f.read().strip()

AWS_CLOUDFRONT_CUSTOM_DOMAIN = 'd1h79sle0i6kpg.cloudfront.net'

# Static storage locs in the bucket
STATICFILES_LOCATION = 'static'

# Media storage locs in the bucket
MEDIAFILES_LOCATION = 'media'

STATICFILES_STORAGE = 'custom_storages.StaticStorage'
STATIC_URL = "https://%s/%s/" % (AWS_CLOUDFRONT_CUSTOM_DOMAIN, STATICFILES_LOCATION)

MEDIA_URL = "https://%s/%s/" % (AWS_CLOUDFRONT_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
