import time
import logging

from ircutils3 import bot
from shownotes import settings

LOGGER = logging.getLogger(__name__)


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

    def message(self,recv, message):
        self.send_message(recv, message)