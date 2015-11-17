import logging
from threading import Thread

from notifyservices.models import Notifylist
from shownotes import settings
from snotes20.models import NUserSocial
from kombu import Connection, Exchange, Queue
from .irc import Ircbot

IRC_EXCHANGE = Exchange('IRC_MESSAGES', 'direct', durable=True)
IRC_QUEUE = Queue('IRC-BOT', exchange=IRC_EXCHANGE, routing_key='irc')


LOGGER = logging.getLogger(__name__)


def send_to_irc(message):
    with Connection(settings.RABBITMQ_URI) as conn:
        # produce
        LOGGER.info("send to irc")
        producer = conn.Producer(serializer='pickle')
        producer.publish(message, exchange=IRC_EXCHANGE, routing_key='irc', declare=[IRC_QUEUE])
        producer.close()


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
        recipients = []
        recipients_user = Notifylist.objects.filter(type=self.type).values('user_id')
        recipients_user = NUserSocial.objects.filter(user_id=recipients_user).filter(type_id=self.type).values('value')

        for r in recipients_user:
            recipients.append(r['value'])
        for recipient in recipients:
            self.bot.message(recipient, "Hallo " + recipient + ". " + body)
        message.ack()


class AMQPMessageHandlerThread(Thread):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    def run(self):
        with Connection(settings.RABBITMQ_URI) as conn:
            # consume
            with conn.Consumer([IRC_QUEUE], callbacks=[self.bot.process_message], accept=['pickle']) as consumer:
                # Process messages and handle events on all channels
                while True:
                    conn.drain_events()


