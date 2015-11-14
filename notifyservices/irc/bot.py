import time
from ircutils3 import bot
from shownotes import settings

class Ircbot(bot.SimpleBot):
    def __init__(self,recipients,message):
        self.nick = settings.IRC_NICK
        self.passwd = settings.IRC_PASSWD
        self.real_name = settings.IRC_REALNAME
        self.server = settings.IRC_SERVER
        self.port = settings.IRC_PORT
        self.mychannels = settings.IRC_CHANNELS
        self.reconnects = 0
        self.message = message
        self.recipients = recipients
        self.ready = False
        bot.SimpleBot.__init__(self, self.nick)
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
            time.sleep(1)
            for recipient in self.recipients:
                print(recipient)
                self.send_message(recipient, "Hallo " + recipient + ". " + self.message)
            self.ready = True
            time.sleep(1)
            self.disconnect()

    def on_ctcp_version(self, event):
        self.send_ctcp_reply(event.source, "VERSION", ["Shownot.es Bot v0"])

    def on_message(self, event):
        pass

    def on_disconnect(self, event):
        if self.reconnects < 3 and not self.ready:
            time.sleep(6)
            self.reconnects += 1
            self.connect(self.server, port=self.port)
        else:
            self.disconnect()