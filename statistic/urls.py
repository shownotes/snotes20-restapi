from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework import routers

from statistic.views import WordFrequencyViewSet

statistic_router = routers.DefaultRouter()
statistic_router.register(r'wordfrequency', WordFrequencyViewSet, base_name='statistic/wordfrequencies')

urlpatterns = patterns('statistic.views',
    url(r'^', include(statistic_router.urls)),
)