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
    For listing or retrieving cosine similarities between podcasts.
    ---
    retrieve:
        parameters:
            - name: pk
              type: string
              description: Podcast slug
              required: true
              paramType: path
        produces:
        - application/json
    """
    def retrieve(self, request, pk=None):
        pod = get_object_or_404(Podcast, slugs__slug=pk)
        podcast_list = PodcastCosineSimilarity.objects.filter(podcastx=pod)

        nodes = []
        links = []

        if pod.cover:
            nodes.append({"name":pod.slug, "coverfile":str(pod.cover)})
        else:
            nodes.append({"name":pod.slug, "coverfile":MEDIA_URL+"cover-placeholder.png"})

        for item in podcast_list:
            # create nodes
            cover = item.podcasty.cover
            if item.podcasty.cover:
                nodes.append({"name":item.podcasty.slug, "coverfile":str(item.podcasty.cover)})
            else:
                nodes.append({"name":item.podcastx.slug, "coverfile":MEDIA_URL+"cover-placeholder.png"})

            links.append({"source":item.podcastx.slug, "target":item.podcasty.slug, "value":item.cosine_sim})

        #print(nodes)
        #print(links)
        objects = {"nodes":nodes,"links":links}
        return Response(objects)

    def list(self, request):
        nodes = []
        links = []

        uniq_podcasts = PodcastCosineSimilarity.objects.all().distinct()
        for item in uniq_podcasts:
            # create nodes
            if item.podcastx.cover:
                nodes.append({"name":item.podcastx.slug, "coverfile":str(item.podcastx.cover)})
            else:
                nodes.append({"name":item.podcastx.slug, "coverfile":MEDIA_URL+"cover-placeholder.png"})
            links.append({"source":item.podcastx.slug, "target":item.podcasty.slug, "value":item.cosine_sim})

        #print(nodes)
        #print(links)
        objects = {"nodes":nodes,"links":links}

        return Response(objects)