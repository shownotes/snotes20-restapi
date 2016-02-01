import logging

# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets
from shownotes.settings import MAX_WORD_FREQUENCIES
from django.db.models import Sum
from statistic.models import WordFrequency
from statistic.serializers import WordListSerializer

logger = logging.getLogger(__name__)


class WordListPodcastViewSet(viewsets.ViewSet):
    """
    For listing or retrieving word lists of podcasts.
    ---
    retrieve:
        parameters:
            - name: top
              type: integer
              description: Reduce output to top x words
              required: false
              paramType: query
            - name: pk
              type: string
              description: Podcast slug
              required: true
              paramType: path
    """
    def retrieve(self, request, pk=None):
        words = WordFrequency.objects.filter(podcast__slugs__slug=pk).values('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse()

        if 'top' in request.QUERY_PARAMS:
            top = int(request.QUERY_PARAMS['top'])
            if top > MAX_WORD_FREQUENCIES:
                top = MAX_WORD_FREQUENCIES
        else:
            top = MAX_WORD_FREQUENCIES

        serializer = WordListSerializer(words[:top],many=True)
        return Response(serializer.data)