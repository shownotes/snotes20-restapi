# snotes20

## Setup
```
$ git clone git@github.com:shownotes/snotes20-restapi.git
$ cd snotes20-restapi
$ virtualenv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
   # create local_settings.py (see below)
$ python manage.py migrate
$ python manage.py loaddata OSFTag.yaml
$ python manage.py loaddata NUserSocialType.yaml
$ python manage.py createsuperuser
```

In addition, you will need a postgresql-server.

## Settings
Create a `./shownotes/local_settings.py`-file and put something like the following in it.
```
SECRET_KEY = ''

# if this is a development-config
DEBUG = True
TEMPLATE_DEBUG = True

CORS_ORIGIN_WHITELIST = (
    'localhost',
    'localhost:9000',
)

ALLOWED_HOSTS = [
    'localhost'
]

EDITORS = {
    'EP': {
      "secret": "fooooo",
      "userurl": "http://localhost:9001/p",
      "apiurl": "http://localhost:9001/api"
    }
}

# Database settings
# https://docs.djangoproject.com/en/dev/ref/databases/

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
    }
}

SITEURL = "http://localhost:9000"

DEFAULT_FROM_EMAIL = 'noreply@localhost'

EMAIL_HOST = 'mail.goooogle.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True

ARCHIVE_RECENT_COUNT = 5

RABBITMQ_ENABLED = False
RABBITMQ_URI = 'amqp://guest:guest@127.0.0.1:5672/%2F'
```

## dev server
To start the development server at http://127.0.0.1:8000/ execute:
```
$ . venv/bin/activate
$ python manage.py runserver
```

## email
You need an SMTP server to send registration-emails. Configure your connection details in `shownotes/local_settings.py` (`EMAIL_*`).

## etherpad
You need a running etherpad instance. Once this is done, configure the API-secret in `shownotes/local_settings.py`.

```
$ git clone git@github.com:ether/etherpad-lite.git
$ cd etherpad-lite
$ ./bin/run.sh
```

The API-secret can be found in `etherpad-lite/APIKEY.txt`.

## amqp

snotes20 publishes a number of events via amqp. The following keys must be set in `local_settings.py`:
* `RABBITMQ_ENABLED = True`,
* `RABBITMQ_URI = 'amqp://guest:guest@127.0.0.1:5672/%2F'`
