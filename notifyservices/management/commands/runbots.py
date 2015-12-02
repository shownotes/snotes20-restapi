import logging

from django.core.management.base import BaseCommand
from notifyservices import Bot_Factory
from shownotes import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = 'Start bots'

    def handle(self, *args, **options):
        if settings.IRC_ENABLED:
            Bot_Factory(type='irc')
            logger.info("IRC bot started")
        logger.info("All bots started")