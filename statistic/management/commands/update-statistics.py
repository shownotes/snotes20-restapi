#!/usr/bin/env python
import logging

from django.db.models import Sum
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import TruncatedSVD

from snotes20.models import Episode, Podcast
from statistic.models import WordFrequency, SignificantPodcastWords, PodcastCosineSimilarity
from django.core.management.base import BaseCommand
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Calculate/Update TF/IDF Tables'

    def handle(self, *args, **options):

        corpus = []
        freq_term_matrix = []
        podcasts = WordFrequency.objects.distinct().values_list('podcast',flat=True)
        tfidf = TfidfTransformer()

        #print('Gesamtzahl von Podcasts mit Publikationen: ', len(podcasts))
        for podcast in podcasts:
            words = dict(WordFrequency.objects.filter(podcast=podcast).values_list('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse())
            #print(Podcast.objects.get(pk=podcast).slug)
            #print(len(words))
            #for w in words:
            #    print(podcast, end='')
            #    print(' ', w, words[w])
            #print("==================")
            corpus.append(words)

        #print("== == == == == == == == == ==\n")

        # train
        v = DictVectorizer(sparse=True)
        X = v.fit_transform(corpus)
        matrix = tfidf.fit_transform(X)
        #print(matrix)

        #print("IDF:", tfidf.idf_) #weights
        #for t in tfidf.idf_[:4]:
        #    print(str(pname) + "\t\t\t\t" + str(t))

        # test
        for i, podcast in enumerate(podcasts):
            p = Podcast.objects.get(pk=podcast)

            print('Verarbeite Publikationen des Podcasts: ', p, '(',str(i),')')
            print("== == == == == == == == == ==")
            words = dict(WordFrequency.objects.filter(podcast=podcast).values_list('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse())
            freq_term_matrix = v.transform([words])

            # 0/1 vector with features in podcast
            #print(freq_term_matrix.todense())

            # get feature names
            feature_names = v.get_feature_names()
            #print(feature_names[:4])

            response = tfidf.transform(freq_term_matrix)

            for feature in response.nonzero()[1]:
                # build update / aysnc over task
                obj = SignificantPodcastWords(podcast=p, word=feature_names[feature], significance=response[0,feature])
                #print(".", end='')
                obj.save()
            #print("\n")

            # cosine similarity
            sims = cosine_similarity(matrix[i:i+1], matrix)
            for j, sim in enumerate(sims.tolist()[0]):
                py = Podcast.objects.get(pk=podcasts[j])
                obj = PodcastCosineSimilarity(podcastx=p, podcasty=py, cosine_sim=sim)
                obj.save()
                #print(p, py, sim)
            print("===============================\n\n")
