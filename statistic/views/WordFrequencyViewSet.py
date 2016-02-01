import logging

# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets
from shownotes.settings import MAX_WORD_FREQUENCIES
from django.db.models import Sum
from statistic.models import WordFrequency
from statistic.serializers import WordFrequencySerializer

logger = logging.getLogger(__name__)


class WordFrequencyViewSet(viewsets.ViewSet):
    """
    For listing word frequencies over all shownotes.
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

        serializer = WordFrequencySerializer(words[:top], many=True)
        return Response(serializer.data)

