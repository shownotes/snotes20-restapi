import logging

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import list_route
from shownotes.settings import MAX_WORD_FREQUENCIES
from django.db.models import Sum
from statistic.models import WordFrequency
from statistic.serializers import WordFrequencySerializer

from .tasks import add_test

logger = logging.getLogger(__name__)


class WordFrequencyViewSet(viewsets.ViewSet):
    """
    For listing or retrieving overall word frequencies.
    ---
    list:
        parameters:
            - name: top
              type: integer
              description: Reduce output to top x words
              required: false
              paramType: query
            - name: word
              type: string
              description: Reduce to a specific word
              required: false
              paramType: query
    """

    def list(self, request):
        words = WordFrequency.objects.values('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse()

        if 'top' in request.QUERY_PARAMS:
            top = int(request.QUERY_PARAMS['top'])
            if top > MAX_WORD_FREQUENCIES:
                top = MAX_WORD_FREQUENCIES
        else:
            top = MAX_WORD_FREQUENCIES

        if 'word' in request.QUERY_PARAMS:
            word = request.QUERY_PARAMS['word'].lower()
            words = words.filter(word=word)

        serializer = WordFrequencySerializer(words[:top],many=True)
        return Response(serializer.data)

    #def retrieve(self, request, pk=None):
    #    word = get_object_or_404(WordFrequency, pk=pk)
    #    serializer = WordFrequencySerializer(word)
    #    return Response(serializer.data)

    """
    retrieve:
        parameters:
            - name: pk
              type: integer
              description: Returns a specific database entry
              required: true
              paramType: form
    """