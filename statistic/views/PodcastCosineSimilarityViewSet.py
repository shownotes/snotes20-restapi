import logging

# Create your views here.
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from shownotes.settings import MAX_SIGIFICANT_WORDS, MEDIA_URL
from snotes20.models import Podcast, Cover
from statistic.models import PodcastCosineSimilarity
from statistic.serializers import SignificantWordsSerializer

logger = logging.getLogger(__name__)

class PodcastCosineSimilarityViewSet(viewsets.ViewSet):
    """
    For listing or retrieving cosine similarities between all podcasts.
    ---
    list:
        parameters:
            - name: threshold
              type: float
              description: Threshold for sigificance values
              required: false
              paramType: query
        produces:
        - application/json
        serializer: SignificantWordsSerializer

    """
    def list(self, request):
        nodes = []
        links = []

        uniq_podcasts = Podcast.objects.filter(id__in=PodcastCosineSimilarity.objects.values_list('podcastx')).distinct()

        for podcast in uniq_podcasts:
            # create nodes
            if podcast.cover:
                nodes.append({"name":podcast.slug, "coverfile":str(podcast.cover)})
            else:
                nodes.append({"name":podcast.slug, "coverfile":MEDIA_URL+"cover-placeholder.png"})

        # create links
        podcast_list = PodcastCosineSimilarity.objects.all()
        for item in podcast_list:
            links.append({"source":item.podcastx.slug, "target":item.podcasty.slug, "value":item.cosine_sim})

        #print(nodes)
        #print(links)
        objects = {"nodes":nodes,"links":links}

        #if 'top' in request.QUERY_PARAMS:
        #    top = int(request.QUERY_PARAMS['top'])
        #    if top > MAX_SIGIFICANT_WORDS:
        #        top = MAX_SIGIFICANT_WORDS
        #else:
        #    top = MAX_SIGIFICANT_WORDS
        #
        #serializer = SignificantWordsSerializer(words[:top],many=True)
        #return Response(serializer.data)

        return Response(objects)