# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import os

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = bool(os.environ.get('DEBUG', 'False'))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ['DB_PORT'])
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

SECRET_KEY = os.environ['SECRET_KEY']

DOCUMENT_DIR = os.path.abspath(os.environ['DOCUMENT_DIR'])

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'core.apps.CoreConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
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

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'server.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'NAME': DB_NAME,
        'OPTIONS': {
            'sslmode': 'require',
            'server_side_binding': True,
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'plain': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'plain'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'asyncio': {
            'level': 'WARNING',
        },
        'django': {
            'level': LOG_LEVEL,
        },
        'django.utils.autoreload': {
            'level': 'INFO',
        },
    },
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True

DATETIME_FORMAT = 'Y-m-d H:i:s'
SHORT_DATETIME_FORMAT = 'Y-m-d H:i:s'
DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'H:i:s'

STATIC_URL = 'static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
