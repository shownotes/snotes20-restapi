"""
Django settings for shownotes project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# Application definition

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_swagger',
    'django_extensions',
    'corsheaders',
    'rules.apps.AutodiscoverRulesConfig',
    'snotes20',
    'djcelery',
    'notifyservices',
    'statistic',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'shownotes.urls'

WSGI_APPLICATION = 'shownotes.wsgi.application'

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
#    'DEFAULT_PERMISSION_CLASSES': [
#        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
#    ]
}

SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.23',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    'api_key': 'foobar',
    'is_authenticated': False,
    'is_superuser': False,
    'permission_denied_handler': None,
    'resource_access_handler': None,
    #'base_path':'http://snotes20.com:8000/api-doc',
    'info': {
        'contact': 'intern@shownot.es',
        'description': 'This is the API documenation of Shownot.es. '
                       'More information at '
                       '<a href="https://shownot.es">'
                       'https://shownot.es</a> '
                       'or on irc.freenode.net, #shownotes. ',
        #'license': 'Apache 2.0',
        #'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
        #'termsOfServiceUrl': 'http://helloreverb.com/terms/',
        'title': 'Shownot.es API',
    },
    'doc_expansion': 'none',
}


# Logging
# https://docs.djangoproject.com/en/1.7/topics/logging/

LOGGING = {
    'version': 1,
    'handlers': {
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'snotes20.management.commands.importexternal': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'snotes20.management.commands.refreshdocstate': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'snotes20.showpadauth.NModelBackend',
    'snotes20.showpadauth.ShowPadBackend'
)

PASSWORD_HASHERS = (
    'snotes20.showpadauth.NPBKDF2PasswordHasher',
)

SITEURL = ""

EMAILS = {
    'activation': {
        'subject': {
            'en': 'shownot.es account activation',
            'de': 'shownot.es Kontoaktivierung',
        }
    },
    'newmail_confirmation': {
        'subject': {
            'en': 'shownot.es email confirmation',
            'de': 'shownot.es Emailbestätigung',
        }
    },
    'pwreset': {
        'subject': {
            'en': 'shownot.es password reset',
            'de': 'shownot.es Passwortreset',
        }
    }
}

DEFAULT_FROM_EMAIL = ''

EMAIL_HOST = ''
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True


TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    BASE_DIR + '/snotes20/emailtemplates/',
)


# for CORS-Headers via CorsMiddleware
CORS_ALLOW_CREDENTIALS = True


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

# custom user model
AUTH_USER_MODEL = 'snotes20.NUser'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'


NOTIFYSERVICE = False
RABBITMQ_URI = 'amqp://guest:passwd@localhost:5672/%2F'
PRIVATE_API_SECRET = "EXAMPLE"

IRC_ENABLED = False
IRC_NICK = 'FooBar'
IRC_PASSWD = 'barz'
IRC_REALNAME = 'Foo Bar'
IRC_SERVER = 'irc.freenode.net'
IRC_PORT = 6667
IRC_CHANNELS = "#shownotes"

# import deployment settings form local_settings.py
try:
    from .local_settings import *
except ImportError:
    print('could not load local settings from local_settings.py')
    raise
