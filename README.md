# snotes20

## Requirements
- Ubuntu 14.04
```sh
sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
```

## Setup
```sh
$ git clone git@github.com:shownotes/snotes20-restapi.git
$ cd snotes20-restapi
$ virtualenv -p /PATH/TO/python3.4 venv
$ source venv/bin/activate
$ pip install -r requirements.txt

$  # Copy either of the 'shownotes/local_settings.py.tpl_*'-files to 'shownotes/local_settings.py' and adapt

$ # Install and configure PostgreSql
$ # Install and configure Etherpad
$ # Install and configure RabbitMQ

$ python manage.py migrate
$ python manage.py loaddata OSFTag.yaml
$ python manage.py loaddata NUserSocialType.yaml
$ python manage.py collectstatic (only for deployment)
$ python manage.py createsuperuser
```


## PostgreSql

You will need a postgresql server with a user and a predefined database,
Alter the database entry in local_settings.py.

```
$ sudo -u postgres createuser -P -d USERNAME
$ sudo -u postgres createdb -O USERNAME DATABASENAME 
```

## Etherpad
You need a running etherpad instance. Once this is done, configure the API-secret in `shownotes/local_settings.py`.

```sh
$ git clone git@github.com:ether/etherpad-lite.git
$ cd etherpad-lite
$ ./bin/run.sh
```

The API-secret can be found in `etherpad-lite/APIKEY.txt`.


## AMQP and RabbitMQ

snotes20 publishes a number of events via AMQP and will need RabbitMQ as broker for asynchronous tasks via celery plugin.

The following keys must be set in `local_settings.py`:
* `NOTFIYSERVICE_ENABLED = True`,
* `RABBITMQ_URI = 'amqp://guest:guest@127.0.0.1:5672/%2F'`

Enable Management Plugin in RabbitMQ configuration and add the user and password from local_settings.py.

### Enable IRC Bot (optional)

The following keys must be set in `local_settings.py`:
* `IRC_ENABLED = True`,
* `RABBITMQ_URI = 'amqp://guest:guest@127.0.0.1:5672/%2F'`


## Email (optional for development)

You need an SMTP server to send registration-emails. Configure your connection details in `shownotes/local_settings.py` (`EMAIL_*`).


## Development Server
To start the development server at http://127.0.0.1:8000/ execute:
```sh
$ source venv/bin/activate
$ python manage.py runserver

$ # Start Celery worker in a new terminal
$ source venv/bin/activate
$ celery -A shownotes worker -l info

$ # Start Shownotes Frontend as shown in https://github.com/shownotes/snotes20-angular-webapp

$ # Run IRC-Bot if enabled
$ source venv/bin/activate 
$ python manage.py runbots
```
