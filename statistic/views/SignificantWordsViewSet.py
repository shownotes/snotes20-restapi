import logging

# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets
from shownotes.settings import MAX_WORD_FREQUENCIES
from django.db.models import Sum
from statistic.models import WordFrequency
from statistic.serializers import WordListSerializer

logger = logging.getLogger(__name__)

class SignificantWordsViewSet(viewsets.ViewSet):
    """
    For listing or retrieving significant words list.
    ---
    list:
        parameters:
            - name: podcast-id
              type: uuid
              description: Reduce output a specific podcast
              required: true
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

        serializer = WordListSerializer(words[:top],many=True)
        return Response(serializer.data)
