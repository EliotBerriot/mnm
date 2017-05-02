# -*- coding: utf-8 -*-
"""
Django settings for mnm project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
import environ

ROOT_DIR = environ.Path(__file__) - 3  # (mnm/config/settings/base.py - 3 = mnm/)
APPS_DIR = ROOT_DIR.path('mnm')

# Load operating system environment variables and then prepare to use them
env = environ.Env()

# .env file, should load only in development environment
READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)

if READ_DOT_ENV_FILE:
    # Operating System Environment variables have precedence over variables defined in the .env file,
    # that is to say variables from the .env files will only be used if not defined
    # as environment variables.
    env_file = str(ROOT_DIR.path('.env'))
    print('Loading : {}'.format(env_file))
    env.read_env(env_file)
    print('The .env file has been loaded. See base.py for more information')

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
]
THIRD_PARTY_APPS = [
    'crispy_forms',  # Form layouts
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'dynamic_preferences',
    'cachalot',
]

# Apps specific for this project go here.
LOCAL_APPS = [
    # custom users app
    'mnm.common',
    'mnm.users.apps.UsersConfig',
    'mnm.instances',
    'mnm.statuses',
    'mnm.client',
    'mnm.bot',
    'mnm.releases',
    'mnm.faq',
    # Your stuff: custom apps go here
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'mnm.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ("""Eliot Berriot""", 'contact@eliotberriot.com'),
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///mnm'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
                'mnm.instances.context_processors.instances_count',
                'mnm.releases.context_processors.releases',
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(APPS_DIR.path('static')),
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

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

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'mnm.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'mnm.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'


INSTALLED_APPS += ['mnm.taskapp.celery.CeleryConfig']
BROKER_URL = env('CELERY_BROKER_URL', default='django://')
if BROKER_URL == 'django://':
    CELERY_RESULT_BACKEND = 'redis://'
else:
    CELERY_RESULT_BACKEND = BROKER_URL


# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

INFLUXDB_URL = env("INFLUXDB_URL", default=None)
INFLUXDB_UDP_PORT = env.int("INFLUXDB_UDP_PORT", default=None)
FETCH_DELAY = env.int('FETCH_DELAY', default=300)
FETCH_COUNTRY_DELAY = env.int('FETCH_COUNTRY_DELAY', default=300)
REFRESH_COUNTRY_DELAY = env.int('REFRESH_COUNTRY_DELAY', default=3000)

CELERY_ROUTES = {
    'mnm.instances.tasks.*': {'queue': 'crawl'},
    'mnm.releases.tasks.*': {'queue': 'crawl'},
    'mnm.bot.tasks.*': {'queue': 'messaging'},
    'mnm.statuses.tasks.*': {'queue': 'statuses'},
}

CELERYBEAT_SCHEDULE = {
    # crontab(hour=0, minute=0, day_of_week='saturday')
    'fetch_from_instances_xyz': {
        'task': 'mnm.instances.tasks.fetch_from_instances_xyz',
        'schedule': crontab(minute='*/5'),
        'options': {
            'expires': 300,
        },
    },
    'fetch_instances_info': {
        'task': 'mnm.instances.tasks.fetch_instances_info',
        'schedule': crontab(minute='*/30'),
        'args': (None, ),
        'options': {
            'expires': 60 * 30,
        },
    },
    'fetch_instances_5m': {
        'task': 'mnm.instances.tasks.fetch_instances',
        'schedule': crontab(minute='*/5'),
        'args': ('instances',),
        'options': {
            'expires': 300,
        },
    },
    'fetch_releases': {
        'task': 'mnm.releases.tasks.fetch_and_import_releases',
        'schedule': crontab(minute='*/5'),
        'options': {
            'expires': 300,
        },
    },
    'fetch_instances_1h': {
        'task': 'mnm.instances.tasks.fetch_instances',
        'schedule': crontab(minute=0, hour='*'),
        'args': ('instances_hourly',),
        'options': {
            'expires': 3600,
        },
    },
    'fetch_instances_1d': {
        'task': 'mnm.instances.tasks.fetch_instances',
        'schedule': crontab(minute=0, hour=0),
        'args': ('instances_daily',),
        'options': {
            'expires': 3600 * 24,
        },
    },
    'fetch_instances_countries_empty': {
        'task': 'mnm.instances.tasks.fetch_instances_countries',
        'schedule': crontab(minute='*/5'),
        'kwargs': {
            'empty': True,
            'maximum': 10,
        },
        'options': {
            'expires': 300,
        },
    },
    'refresh_instances_country': {
        'task': 'mnm.instances.tasks.fetch_instances_countries',
        'schedule': crontab(minute=0),
        'kwargs': {
            'empty': False,
            'maximum': 10,
        },
        'options': {
            'expires': 3600,
        },
    },
}

STATUSES_RECORD = {
    'client_id': env('STATUSES_RECORD_CLIENT_ID', default=''),
    'client_secret': env('STATUSES_RECORD_CLIENT_SECRET', default=''),
    'access_token': env('STATUSES_RECORD_ACCESS_TOKEN', default=''),
    'api_base_url': env('STATUSES_RECORD_URL', default=''),
}

STATS_BOT = {
    'client_id': env('STATS_BOT_CLIENT_ID', default=''),
    'name': env('STATS_BOT_name', default='mnm'),
    'client_secret': env('STATS_BOT_CLIENT_SECRET', default=''),
    'access_token': env('STATS_BOT_ACCESS_TOKEN', default=''),
    'api_base_url': env('STATS_BOT_URL', default=''),
}

NOTIFY_ON_RELEASE = env.bool('NOTIFY_ON_RELEASE', default=True)
