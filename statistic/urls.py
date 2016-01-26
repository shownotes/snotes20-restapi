import statistic.views
from django.conf.urls import patterns, include, url
from rest_framework import routers
import statistic.views

statistic_router = routers.DefaultRouter()
statistic_router.register(r'wordfrequency', statistic.views.WordFrequencyViewSet, base_name='statistic/wordfrequencies')
statistic_router.register(r'wordlist', statistic.views.WordListViewSet, base_name='statistic/wordlist')
statistic_router.register(r'timeline-podcast', statistic.views.TimeLinePodcastsViewSet, base_name='statistic/timeline')
statistic_router.register(r'podcast', statistic.views.PodcastListViewSet, base_name='statistic/archive')

urlpatterns = patterns('statistic.views',
                       url(r'^', include(statistic_router.urls)),
                       )