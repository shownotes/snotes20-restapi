import logging

# Create your views here.
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from shownotes.settings import MAX_SIGIFICANT_WORDS
from snotes20.models import Podcast
from statistic.models import SignificantPodcastWords, WordFrequency
from statistic.serializers import SignificantWordsSerializer

logger = logging.getLogger(__name__)

class SignificantPodcastWordsViewSet(viewsets.ViewSet):
    """
    For listing or retrieving significant words list of a specific podcast.
    ---
    retrieve:
        parameters:
            - name: pk
              type: string
              description: Podcast slug
              required: true
              paramType: path
            - name: top
              type: integer
              description: Reduce output to x top ranked values
              required: false
              paramType: query
        produces:
        - application/json
        serializer: SignificantWordsSerializer

    """
    def retrieve(self, request, pk=None):
        podcast = get_object_or_404(Podcast, slugs__slug=pk)
        words = SignificantPodcastWords.objects.filter(podcast=podcast).order_by('significance').reverse()
        p = WordFrequency.objects.filter(podcast=podcast).values('word').annotate(frequency=Sum('frequency')).order_by('frequency').reverse()

        if 'top' in request.QUERY_PARAMS:
            top = int(request.QUERY_PARAMS['top'])
            if top > MAX_SIGIFICANT_WORDS:
                top = MAX_SIGIFICANT_WORDS
        else:
            top = MAX_SIGIFICANT_WORDS

        serializer = SignificantWordsSerializer(words[:top],many=True)
        return Response(serializer.data)