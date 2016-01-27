from __future__ import absolute_import

from django.db.models import Sum

from shownotes.celery import app

import logging
from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
import string

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfTransformer
from statistic.models import WordFrequency, SignificantPodcastWords, PodcastCosineSimilarity

from snotes20.models import OSFNote, Podcast

logger = logging.getLogger(__name__)

stop_words = set(stopwords.words(['german','english']))
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
        entries = []
        for word in all_words:
            entries.append(WordFrequency(word=word,
                          frequency=all_words[word],
                          relativ_frequency=float(all_words[word]/len(all_words)),
                          episode=episode,
                          podcast=episode.podcast,
                          state=publication.state
            ))
        WordFrequency.objects.bulk_create(entries)
        logger.debug("NEW entry for " + str(episode))

    return True


@app.task
def update_podcast_statistics(i, podcasts, dictvectorizer, tfidf_matrix, tfidf):
    feature_names = dictvectorizer.get_feature_names()
    podcastx = Podcast.objects.get(pk=podcasts[i])

    # calculate tfidf matrix for podcastx i
    logger.debug('Verarbeite Publikationen des Podcasts: ', podcastx)
    words = dict(WordFrequency.objects.filter(podcast=podcastx).values_list('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse())
    freq_term_matrix = dictvectorizer.transform([words])
    response = tfidf.transform(freq_term_matrix)

    # generate significant words for podcastx i and write to database
    entries = []
    for feature in response.nonzero()[1]:
        entries.append(SignificantPodcastWords(podcast=podcastx, word=feature_names[feature], significance=response[0,feature]))
    SignificantPodcastWords.objects.bulk_create(entries)

    # generate cosine similarity for podcastx i to all other matricies
    sims = cosine_similarity(tfidf_matrix[i:i+1], tfidf_matrix)

    # generate objects and write to database
    entries = []
    for j, sim in enumerate(sims.tolist()[0]):
        podcasty = Podcast.objects.get(pk=podcasts[j])
        entries.append(PodcastCosineSimilarity(podcastx=podcastx, podcasty=podcasty, cosine_sim=sim))
    PodcastCosineSimilarity.objects.bulk_create(entries)

    return True