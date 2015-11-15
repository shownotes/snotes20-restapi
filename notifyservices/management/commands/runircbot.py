from django.core.management.base import BaseCommand
from notifyservices.irc import Bot_Factory


class Command(BaseCommand):
    args = ''
    help = 'Start Ircbot'

    def handle(self, *args, **options):
        Bot_Factory()
        print("Running....")
