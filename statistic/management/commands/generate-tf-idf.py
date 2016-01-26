#!/usr/bin/env python
import logging

from django.db.models import Sum
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.decomposition import TruncatedSVD

from snotes20.models import Episode, Podcast
from statistic.models import WordFrequency, SignificantPodcastWords
from django.core.management.base import BaseCommand



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

        # test
        for podcast in podcasts:
            p = Podcast.objects.get(pk=podcast)

            print('Teste auf Publikationen des Podcasts: ', p)
            print("== == == == == == == == == ==\n")
            words = dict(WordFrequency.objects.filter(podcast=podcast).values_list('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse())
            freq_term_matrix = v.transform([words])
            #freq_term_matrix = v.transform([{'leipzig':0.22,'berlin':0.1,'podcast':0.2, 'folge':0.01,'tim':0.6}])

            # 0/1 vector with features in podcast
            #print(freq_term_matrix.todense())

            # get feature names
            feature_names = v.get_feature_names()
            #print(feature_names[:4])

            tfidf.fit_transform(X)
            #print("IDF:", tfidf.idf_) #weights
            #for t in tfidf.idf_[:4]:
            #    print(str(pname) + "\t\t\t\t" + str(t))

            response = tfidf.transform(freq_term_matrix)

            #print(response)
            #print(response.toarray())
            #print(response.todense())
            #print("Signifikate Wörter")
            #for col in response.nonzero()[1]:
            #    if response[0, col] > 0.1:
            #        print(col, ' :', end=' ')
            #        print(feature_names[col], ' - ', response[0, col])
            #print("== == == == == == == == == ==\n")

            for feature in response.nonzero()[1]:
                # build update / aysnc over task
                obj = SignificantPodcastWords(podcast=p, word=feature_names[feature], significance=response[0,feature])
                print(".", end='')
                obj.save()
            print("\n")