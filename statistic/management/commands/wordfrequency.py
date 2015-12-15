#!/usr/bin/env python
import logging
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string

from django.core.management.base import BaseCommand

from snotes20.models import Publication, OSFNote, Episode
from statistic.tasks import update_wordfrequencies

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Calculate word frequencies for existing database entries'

    def handle(self, *args, **options):

        # Get all episodes with existing publications
        episodes = Episode.objects.filter(id__in=Publication.objects.all().values('episode_id'))
        for episode in episodes:
            # Get last publication for episode
            last_publication = Publication.objects.filter(episode=episode).order_by('create_date').reverse()[:1]

            # If no publication to episode or an entry in WordFrequency with same state_id exists
            if last_publication:
                update_wordfrequencies.delay(episode, last_publication[0])
