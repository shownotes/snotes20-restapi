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
punctuations = list(string.punctuation)

class Command(BaseCommand):
    help = 'Recalculate/Calculate word frequencies for database entries'

    def handle(self, *args, **options):
        episodes = Episode.objects.filter(id__in=Publication.objects.all().values('episode_id'))
        for episode in episodes:
            ## publication vergleichen (in model)
            #### update in abhaengigkeit
            last_publication = Publication.objects.filter(episode=episode).order_by('create_date').reverse()[:1]
            if last_publication:
                osfnotes = OSFNote.objects.filter(state_id=last_publication[0].state_id)
                all_osfnotes = self.aggregate_shownotes(osfnotes)


                ## tokenizer kleiner
                episode_words = []
                for sentence in all_osfnotes:
                    word_tokens = word_tokenize(sentence.lower())
                    word_tokens = [w for w in word_tokens if w not in punctuations]
                    word_tokens = [w for w in word_tokens if w not in stop_words]
                    [episode_words.append(w) for w in word_tokens]
                all_words = FreqDist(episode_words)

                ### datenbank update einzeilig
                for word in all_words:
                    if WordFrequency.objects.filter(episode=episode).filter(word=word).exists():
                        logger.debug("UPDATE Entry for " + str(episode) + " with word " + word)
                        entry = WordFrequency.objects.filter(episode=episode).get(word=word)
                        entry.frequency = all_words[word]
                    else:
                        logger.debug("NEW Entry for " + str(episode) + " with word " + word)
                        entry = WordFrequency(word=word, frequency=all_words[word], episode=episode)
                    entry.save()


    def aggregate_shownotes(self, osfnotes):
        all_notes = []
        for note in osfnotes:
            all_notes.append(note.title)
            if OSFNote.objects.filter(parent_id=note.id).exists():
                for subsubnote in self.aggregate_shownotes(OSFNote.objects.filter(parent_id=note.id)):
                    all_notes.append(subsubnote)
        return all_notes