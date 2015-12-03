#!/usr/bin/env python
import logging
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string

from sklearn.feature_extraction.text import TfidfVectorizer
from django.core.management.base import BaseCommand, CommandError

from snotes20.models import Publication, Document, OSFNote, Episode, OSFDocumentState
from statistic.models import WordFrequency

logger = logging.getLogger(__name__)

stop_words = set(stopwords.words('german'))
stop_words.add('http')
stop_words.add('https')
stop_words.add('dass')
# fix for old header...
stop_words.add('HEADER')
stop_words.add('/HEADER')
stop_words.add('Starttime')
stop_words.add('relativeTimestamps')
stop_words.add('Episodepage')

punctuations = list(string.punctuation)
punctuations.append("“")
punctuations.append('\'\'')
punctuations.append('``')
punctuations.append('‒')
punctuations.append('-')
punctuations.append('--')
punctuations.append('---')
punctuations.append('...')

class Command(BaseCommand):
    help = 'Recalculate/Calculate word frequencies for database entries'

    def handle(self, *args, **options):

        #Get all episodes with existing publications
        episodes = Episode.objects.filter(id__in=Publication.objects.all().values('episode_id'))
        for episode in episodes:
            # Get last publication for episode
            last_publication = Publication.objects.filter(episode=episode).order_by('create_date').reverse()[:1]

            # If any and there is no entry with the same state_id in WordFrequency
            if last_publication and not WordFrequency.objects.filter(state=last_publication[0].state).filter(episode=episode).exists():

                # Get all shownotes for last publication
                osfnotes = OSFNote.objects.filter(state_id=last_publication[0].state_id)
                all_osfnotes = self.aggregate_shownotes(osfnotes)

                # Tokenize all words
                episode_words = []
                for sentence in all_osfnotes:
                    word_tokens = word_tokenize(sentence.lower())
                    word_tokens = [w for w in word_tokens if w not in punctuations]
                    word_tokens = [w for w in word_tokens if w not in stop_words]
                    [episode_words.append(w) for w in word_tokens]
                all_words = FreqDist(episode_words)

                # Insert into database
                for word in all_words:
                    logger.debug("NEW Entry for " + str(episode) + " with word " + word)
                    entry = WordFrequency(word=word,
                                          frequency=all_words[word],
                                          relativ_frequency=float(all_words[word]/len(all_words)),
                                          episode=episode,
                                          podcast=episode.podcast,
                                          state=last_publication[0].state
                    ).save()


    def aggregate_shownotes(self, osfnotes):
        all_notes = []
        for note in osfnotes:
            all_notes.append(note.title)
            if OSFNote.objects.filter(parent_id=note.id).exists():
                for subsubnote in self.aggregate_shownotes(OSFNote.objects.filter(parent_id=note.id)):
                    all_notes.append(subsubnote)
        return all_notes