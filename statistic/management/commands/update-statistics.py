#!/usr/bin/env python
import logging

from django.db.models import Sum
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from django.core.management.base import BaseCommand

from statistic.models import WordFrequency, PodcastCosineSimilarity, SignificantPodcastWords
from statistic.tasks import update_podcast_statistics

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Calculate/Update TF/IDF Tables'

    def handle(self, *args, **options):

        PodcastCosineSimilarity.objects.all().delete()
        SignificantPodcastWords.objects.all().delete()

        corpus = []
        podcasts = WordFrequency.objects.distinct().values_list('podcast',flat=True)
        tfidf = TfidfTransformer()

        # Generate corpus
        for podcast in podcasts:
            words = dict(WordFrequency.objects.filter(podcast=podcast).values_list('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse())
            corpus.append(words)

        # train
        v = DictVectorizer(sparse=True)
        X = v.fit_transform(corpus)
        tfidf_matrix = tfidf.fit_transform(X)

        # Write entries to tables
        for i, podcast in enumerate(podcasts):
            update_podcast_statistics.delay(i, podcasts, v, tfidf_matrix, tfidf)
