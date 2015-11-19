# snotes20

## Setup
```
$ git clone git@github.com:shownotes/snotes20-restapi.git
$ cd snotes20-restapi
$ virtualenv -p /PATH/TO/python3.4 venv
$ . venv/bin/activate
$ pip install -r requirements.txt
   # copy either of the 'shownotes/local_settings.py.tpl_*'-files to 'shownotes/local_settings.py' and adapt 
$ python manage.py migrate
$ python manage.py loaddata OSFTag.yaml
$ python manage.py loaddata NUserSocialType.yaml
$ python manage.py collectstatic
$ python manage.py createsuperuser
```

## PostgreSql

You will need a postgresql server with a user and a predefined database

```
$ sudo -u postgres createuser -P -d USERNAME
$ sudo -u postgres createdb -O USERNAME DATABASENAME 
```

Alter the database entry in local_settings.py


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
