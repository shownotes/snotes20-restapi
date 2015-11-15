from __future__ import absolute_import

import os
from celery import Celery, shared_task

#class NotifyServiceRouter(object):
#
#    def route_for_task(self, task, args=None, kwargs=None):
#        if task == 'nofifyservices.tasks.new_document:':
#            return {'exchange': 'DOCUMENT_NEW',
#                    'exchange_type': 'fanout',
#                    'routing_key': 'DOCUMENT'}
#        return None

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shownotes.settings')

from django.conf import settings  # noqa

app = Celery('shownotes',backend='amqp', broker=settings.RABBITMQ_URI)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))