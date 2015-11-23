from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from requests import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from .tasks import add_test

class StatisticViewSet(viewsets.ViewSet):

    def list(self, request):
        return HttpResponse()

    @list_route()
    def wordcloud(self, request):
        add_test.delay(4,4)
        return HttpResponse([{"text":"foo", "size":25}, {"text":"foobar", "size":17}, {"text":"bar", "size":12}, {"text":"shownotes", "size":5}])
