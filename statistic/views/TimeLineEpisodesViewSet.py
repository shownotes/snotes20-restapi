from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

import snotes20.models as models
import snotes20.serializers as serializers

class TimeLineEpisodesViewSet(viewsets.ViewSet):
    """
    For retrieving number of episodes of a podcast per period range (month).
    The last months are returned in descending order.
    ---
    """
    def list(self, request, pk=None):

        from django.db import connection
        cursor = connection.cursor()##

        # Data retrieval operation - no commit required
        cursor.execute(
                ' SELECT COUNT(DISTINCT "snotes20_episode"."id"), concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date))'
                '  FROM "snotes20_episode"'
                '  INNER JOIN "snotes20_publication" ON ("snotes20_episode"."id" = "snotes20_publication"."episode_id")'
                '  INNER JOIN "snotes20_podcast" ON ("snotes20_episode"."podcast_id" = "snotes20_podcast"."id")'
                '  INNER JOIN "snotes20_podcastslug" ON ("snotes20_podcast"."id" = "snotes20_podcastslug"."podcast_id")'
                '  WHERE "snotes20_publication"."create_date" IS NOT NULL'
                '  AND "snotes20_podcastslug"."slug" = \'' + str(pk) + '\''
                '  GROUP BY concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date)) '
                '  ORDER BY concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date)) DESC ;'

        )
        return Response(cursor.fetchall())