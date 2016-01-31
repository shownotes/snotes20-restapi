from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

import snotes20.models as models
import snotes20.serializers as serializers

class EpisodeListViewSet(viewsets.ViewSet):
    """
    For listing or retrieving episodes of a podcast from a specific period.
    ---
    retrieve:
        parameters:
            - name: pk
              type: string
              description: slug from a specific podcast for timeline viewing
              required: true
              paramType: path
            - name: period
              type: string
              description: required format = [M]M-YYYY. Filter to a specific period for timeline viewing
              required: false
              paramType: query
        produces:
        - application/json
    """
    def retrieve(self, request, pk=None):
        get_object_or_404(models.Podcast, slugs__slug=pk)

        period = ''

        data = None

        if 'period' in request.QUERY_PARAMS:
            period = request.QUERY_PARAMS['period']

        try:
            pod = models.Podcast.objects.get(slugs__slug=pk)
            data = serializers.PodcastSerializer(pod).data
        except models.Podcast.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if period:
            period_parts = period.split("-")
            filtered_episodes = []
            for episode in data['episodes']:
                if (int(period_parts[0]) == episode['create_date'].month and
                    int(period_parts[1]) == episode['create_date'].year):
                    filtered_episodes.append(episode)
            data['episodes'] = filtered_episodes
        return Response(data)