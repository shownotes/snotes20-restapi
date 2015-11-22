import logging
from threading import Thread
import json

from notifyservices.models import Notifylist
from kombu import Connection, Queue, Exchange
from .irc import Ircbot

from shownotes import settings
from snotes20.models import NUserSocial

LOGGER = logging.getLogger(__name__)
PUBEXCHANGE = Exchange("Publication", type="direct")
DOCEXHANGE = Exchange("Document", type="direct")
PUBNEW_QUEUE = Queue('IRC-Bot', exchange=PUBEXCHANGE, routing_key='publication.new')
PUBREQ_QUEUE = Queue('IRC-Bot', exchange=PUBEXCHANGE, routing_key='publication.request')
DOCNEW_QUEUE = Queue('IRC-Bot', exchange=DOCEXHANGE, routing_key='document.new')


def Bot_Factory(type=None):
    botthread = None
    if type == 'irc':
        botthread = BotThread(type)
    else:
        raise Exception
    botthread.start()
    return botthread


class BotThread(Thread):
    def __init__(self, type):
        if type == 'irc':
            self.bot = Ircbot()
        self.type = type
        self.amqp = AMQPMessageHandlerThread(self)
        super().__init__()

    def run(self):
        self.amqp.start()
        self.bot.start()

    def process_message(self, body, message):
        msg = None
        recipients = []
        body = json.loads(body)
        if message.delivery_info["routing_key"] == "publication.new":
            msg = "{} hat eine Publikation für {}-{} veröffentlicht.".format(body["issuer"], body["podcast"], body["episodenumber"])
            for channel in settings.IRC_CHANNELS:
                recipients.append(channel)
        elif message.delivery_info["routing_key"] == "publication.request":
            msg = "{} hat einen Publikationsrequest für {}-{} erstellt. Bitte kümmere dich doch darum. :)".format(body["issuer"], body["podcast"], body["episodenumber"])
        elif message.delivery_info["routing_key"] == "document.new":
            msg = "Das Pad {} wurde erstellt.".format(body["name"])
	    #for channel in settings.IRC_CHANNELS:
            # 	recipients.append(channel)
        else:
            return

        recipients_user = Notifylist.objects.filter(type=self.type).values('user_id')
        recipients_user = NUserSocial.objects.filter(user_id=recipients_user).filter(type_id=self.type).values('value')
        for r in recipients_user:
            recipients.append(r['value'])

        for recipient in recipients:
            self.bot.message(recipient, msg)
        message.ack()


class AMQPMessageHandlerThread(Thread):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    def run(self):
        with Connection(settings.RABBITMQ_URI) as conn:
            # consume
            with conn.Consumer([DOCNEW_QUEUE, PUBREQ_QUEUE, PUBNEW_QUEUE], callbacks=[self.bot.process_message], accept=['json']) as consumer:
                # Process messages and handle events on all channels
                while True:
                    conn.drain_events()
