from django.core.management.base import BaseCommand
from notifyservices import Bot_Factory


class Command(BaseCommand):
    args = ''
    help = 'Start Bots'

    def handle(self, *args, **options):
        Bot_Factory(type='irc')
        print("IRC-Bot started")
        print("All bots started")
