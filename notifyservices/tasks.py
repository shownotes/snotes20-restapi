from __future__ import absolute_import

import time

from notifyservices.irc import Ircbot
from celery import task, shared_task
from django.core.cache import cache
from notifyservices.models import Notifylist
from snotes20.models import NUserSocial
from hashlib import md5

LOCK_EXPIRE = 60 * 5 # Lock expires in 5 minutes


@shared_task
def send_to_irc(message):

    recipients = []
    recipients_user = Notifylist.objects.filter(type='irc').values('user_id')
    recipients_user = NUserSocial.objects.filter(user_id=recipients_user).filter(type_id='irc').values('value')

    for r in recipients_user:
        recipients.append(r['value'])

    message_hex = md5(bytes(message, 'utf-8'))
    # The cache key consists of the recipients names
    lock_id = '{0}-lock-{1}'.format(str(time.time()), message_hex.hexdigest())

    # cache.add fails if the key already exists
    acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)

    # memcache delete is very slow, but we have to use it to take
    # advantage of using add() for atomic locking
    release_lock = lambda: cache.delete(lock_id)

    if acquire_lock():
        try:
            ibot = Ircbot(recipients, message)
            ibot.start()
        finally:
            release_lock()
