from django.conf.urls import patterns, include, url
from rest_framework import routers
from statistic.views import WordFrequencyViewSet, WordListViewSet, TimeLinePodcastsViewSet, PodcastListViewSet, SignificantWordsViewSet, TimeLineEpisodesViewSet

statistic_router = routers.DefaultRouter()
statistic_router.register(r'wordfrequency', WordFrequencyViewSet, base_name='statistic/wordfrequencies')
statistic_router.register(r'wordlist', WordListViewSet, base_name='statistic/wordlist')
statistic_router.register(r'significantwords', SignificantWordsViewSet, base_name='statistic/significantwords')

statistic_router.register(r'timeline-podcast', TimeLinePodcastsViewSet, base_name='statistic/timeline-podcast')
statistic_router.register(r'podcast', PodcastListViewSet, base_name='statistic/podcast')
statistic_router.register(r'timeline-episode', TimeLineEpisodesViewSet, base_name='statistic/timeline-episode')

urlpatterns = patterns('statistic.views',
                       url(r'^', include(statistic_router.urls)),
)
