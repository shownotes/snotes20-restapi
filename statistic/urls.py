from django.conf.urls import patterns, include, url
from rest_framework import routers
from statistic.views import WordFrequencyViewSet, WordListViewSet, TimeLinePodcastsViewSet, PodcastListViewSet, TimeLineEpisodesViewSet, PodcastCosineSimilarityViewSet, SignificantPodcastWordsViewSet, EpisodeListViewSet

statistic_router = routers.DefaultRouter()
statistic_router.register(r'podcast', PodcastListViewSet, base_name='statistic/podcast')
statistic_router.register(r'episode', EpisodeListViewSet, base_name='statistic/episode')

statistic_router.register(r'cosinesimilarty/podcast', PodcastCosineSimilarityViewSet, base_name='statistic/cosinesimilarity/podcast')

#statistic_router.register(r'significantwords/episode', SignificantPodcastWordsViewSet, base_name='statistic/significantwords/episode')
statistic_router.register(r'significantwords/podcast', SignificantPodcastWordsViewSet, base_name='statistic/significantwords/podcast')

statistic_router.register(r'timeline/episode', TimeLineEpisodesViewSet, base_name='statistic/timeline/episode')
statistic_router.register(r'timeline/podcast', TimeLinePodcastsViewSet, base_name='statistic/timeline/podcast')

statistic_router.register(r'wordlist', WordListViewSet, base_name='statistic/wordlist')
statistic_router.register(r'wordfrequency', WordFrequencyViewSet, base_name='statistic/wordfrequencies')

urlpatterns = patterns('statistic.views',
                       url(r'^', include(statistic_router.urls)),
)
