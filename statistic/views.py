import logging

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from django.db.models import Sum

from statistic.models import WordFrequency
from statistic.serializers import WordFrequencySerializer

from .tasks import add_test

logger = logging.getLogger(__name__)

class StatisticViewSet(viewsets.ViewSet):

    def list(self, request):
        logger.debug("view on /statistic/")
        return HttpResponse()

    @list_route(methods=['GET'])
    def wordcloud(self, request):
        logger.debug("view on /statistic/wordcloud")
        if 'top' in request.QUERY_PARAMS:
            top = int(request.QUERY_PARAMS['top'])
        else:
            top = 50

        words = WordFrequency.objects.all().order_by('frequency').reverse()[:top]
        # find a efficient way to summup all values in data
        logger.debug(words)
        serializer = WordFrequencySerializer(words,many=True)
        return Response(serializer.data)
