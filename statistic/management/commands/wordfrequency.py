#!/usr/bin/env python
import logging
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from statistic.models import WordFrequency

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Recalculate/Calculate word frequencies for databse entrys'

    def handle(self, *args, **options):
        pass
