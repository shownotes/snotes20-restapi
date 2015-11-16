from threading import Thread
import time
import logging

from kombu import Connection, Exchange, Queue
from ircutils3 import bot

from shownotes import settings
from notifyservices.models import Notifylist
from snotes20.models import NUserSocial

LOGGER = logging.getLogger(__name__)

IRC_EXCHANGE = Exchange('IRC_MESSAGES', 'fanout', durable=True)
IRC_QUEUE = Queue('IRC-BOT', exchange=IRC_EXCHANGE, routing_key='IRC')


def send_to_irc(message):
    with Connection(settings.RABBITMQ_URI) as conn:
        # produce
        LOGGER.info("send to irc")
        producer = conn.Producer(serializer='pickle')
        producer.publish(message, exchange=IRC_EXCHANGE, routing_key='IRC', declare=[IRC_QUEUE])
        producer.close()


def handle_messages(thread):
    with Connection(settings.RABBITMQ_URI) as conn:
        # consume
        with conn.Consumer([IRC_QUEUE], callbacks=[thread.process_message], accept=['pickle']) as consumer:
            # Process messages and handle events on all channels
            while True:
                conn.drain_events()




def Bot_Factory(type=None):
    if type == 'irc':
        th = BotThread(Ircbot())
        th.start()
        return th
    else:
        return None


class BotThread(Thread):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    def run(self):
            self.bot.start()
            handle_messages(thread=self)

    def process_message(self, body, message):
        recipients = []
        recipients_user = Notifylist.objects.filter(type='irc').values('user_id')
        recipients_user = NUserSocial.objects.filter(user_id=recipients_user).filter(type_id='irc').values('value')

        for r in recipients_user:
            recipients.append(r['value'])
        for recipient in recipients:
            self.bot.send_message(recipient, "Hallo " + recipient + ". " + body)
        message.ack()


class Ircbot(bot.SimpleBot):
    def __init__(self):
        self.nick = settings.IRC_NICK
        self.passwd = settings.IRC_PASSWD
        self.real_name = settings.IRC_REALNAME
        self.server = settings.IRC_SERVER
        self.port = settings.IRC_PORT
        self.mychannels = settings.IRC_CHANNELS
        self.reconnects = 0
        bot.SimpleBot.__init__(self, self.nick)
        #self.connect(self.server, port=self.port, channel=self.mychannels)
        self.connect(self.server, port=self.port)

    ### events ###
    def on_any(self, event):
        #print("command:" + event.command)
        #print("params:" + str(event.params))
        if event.command == "ERR_NICKNAMEINUSE":
            self.disconnect()
        if event.command == "RPL_ENDOFMOTD":
            # if self.passwd:
            # self.identify(self.passwd)
            LOGGER.info("IRC-Bot online")
            print("IRC-Bot online")

    def on_ctcp_version(self, event):
        self.send_ctcp_reply(event.source, "VERSION", ["Shownot.es Bot v0"])

    def on_message(self, event):
        pass

    def on_disconnect(self, event):
        if self.reconnects < 3:
            LOGGER.info("reconnect...")
            time.sleep(6)
            self.reconnects += 1
            self.connect(self.server, port=self.port)
        else:
            LOGGER.info("IRC-Bot offline")
            self.disconnect()
