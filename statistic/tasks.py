from __future__ import absolute_import
from shownotes.celery import app

import logging
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string

from sklearn.feature_extraction.text import TfidfVectorizer

from snotes20.models import OSFNote
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

@app.task
def update_wordfrequencies(episode, publication):

    def aggregate_shownotes(osfnotes):
        all_notes = []
        for note in osfnotes:
            all_notes.append(note.title)
            if OSFNote.objects.filter(parent_id=note.id).exists():
                for subsubnote in aggregate_shownotes(OSFNote.objects.filter(parent_id=note.id)):
                    all_notes.append(subsubnote)
        return all_notes

    # If no publication to episode or an entry in WordFrequency with same stae_id exists
    if not WordFrequency.objects.filter(state=publication.state).filter(episode=episode).exists():

        if WordFrequency.objects.filter(episode=episode).exists():
            # Delete entries
            WordFrequency.objects.filter(episode=episode).delete()
            logger.debug("Delete on update for " + str(episode))

        # Get all shownotes for last publication
        osfnotes = OSFNote.objects.filter(state_id=publication.state_id)
        all_osfnotes = aggregate_shownotes(osfnotes)

        # Tokenize all words
        episode_words = []
        for sentence in all_osfnotes:
            word_tokens = word_tokenize(sentence.lower())
            word_tokens = [w for w in word_tokens if w not in punctuations]
            word_tokens = [w for w in word_tokens if w not in stop_words]
            [episode_words.append(w) for w in word_tokens]
        all_words = FreqDist(episode_words)

        # Save entries
        for word in all_words:
            WordFrequency(word=word,
                          frequency=all_words[word],
                          relativ_frequency=float(all_words[word]/len(all_words)),
                          episode=episode,
                          podcast=episode.podcast,
                          state=publication.state
            ).save()
        logger.debug("NEW entry for " + str(episode))

    return True
