from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

import snotes20.models as models
import snotes20.serializers as serializers

class TimeLineEpisodesViewSet(viewsets.ViewSet):
    """
    For retrieving number of episodes of a podcast per period range (month). The last months are returned in descending order.
    ---
    retrieve:
        parameters:
            - name: pk
              type: string
              description: slug from a specific podcast for timeline viewing
              required: true
              paramType: path
        produces:
        - application/json
    """
    def retrieve(self, request, pk=None):
        podcast = get_object_or_404(models.Podcast, slugs__slug=pk)

        from django.db import connection
        cursor = connection.cursor()##

        # Data retrieval operation - no commit required
        cursor.execute(
                ' SELECT COUNT(DISTINCT "snotes20_episode"."id"), concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date)) as filter_date'
                '  FROM "snotes20_episode"'
                '  INNER JOIN "snotes20_podcast" ON ("snotes20_episode"."podcast_id" = "snotes20_podcast"."id")'
                '  INNER JOIN "snotes20_podcastslug" ON ("snotes20_podcast"."id" = "snotes20_podcastslug"."podcast_id")'
                '  WHERE "snotes20_episode"."create_date" IS NOT NULL'
                '  AND "snotes20_podcastslug"."slug" = \'' + str(pk) + '\''
                '  GROUP BY filter_date ;'

        )
        return Response(cursor.fetchall())