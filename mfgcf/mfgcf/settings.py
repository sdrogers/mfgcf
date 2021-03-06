"""
Django settings for mfgcf project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import distutils.util as du

def getNeededString(name):
    if not os.environ.has_key(name):
        raise Exception('Environment variable ' + name + ' is needed but is not defined')
    return os.environ[name]

def getString(name, default):
    if not os.environ.has_key(name):
        return default
    return os.environ[name]

def getBool(name, default):
    if not os.environ.has_key(name):
        return default
    return bool(du.strtobool(os.environ[name]))

def getList(name, default):
    if not os.environ.has_key(name):
        return default
    return os.environ[name].split(',')


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z$0kae=$hkdy9=n@(nb9umafzg0q5q#y(6r6981-y&$0-+7u^s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getBool('DEBUG', True)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']


# Application definition

INSTALLED_APPS = [
    'django_markdown2',    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chunked_upload',
    'linker',
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

ROOT_URLCONF = 'mfgcf.urls'
LOGIN_REDIRECT_URL = 'home'

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

WSGI_APPLICATION = 'mfgcf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASE_ENGINE = getString('DATABASE_ENGINE', 'django.db.backends.sqlite3')
if DATABASE_ENGINE == 'django.db.backends.mysql':
    DATABASE_NAME = getNeededString('MYSQL_DATABASE')
    DATABASE_USER = getNeededString('MYSQL_USER')
    DATABASE_PASSWORD = getNeededString('MYSQL_PASSWORD')
elif DATABASE_ENGINE == 'django.db.backends.sqlite3':
    SQLITE_DATABASE_FILENAME = getString('SQLITE_DATABASE_FILENAME', 'db.sqlite3')
    DATABASE_NAME = os.path.join(BASE_DIR, SQLITE_DATABASE_FILENAME)
    DATABASE_USER = ''
    DATABASE_PASSWORD = ''

DATABASES = {
    'default': {
        'ENGINE': DATABASE_ENGINE,
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': DATABASE_PASSWORD,                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_PATH = os.path.join(BASE_DIR,'static')
STATIC_ROOT = getString('STATIC_ROOT', os.path.join(BASE_DIR,'assets'))

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    STATIC_PATH,
)

