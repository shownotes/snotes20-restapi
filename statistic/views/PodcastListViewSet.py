import operator

from django.conf import settings
from django.db.models import Q
from functools import reduce
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route

import snotes20.models as models
import snotes20.serializers as serializers

class PodcastListViewSet(viewsets.ViewSet):
    def list(self, request):
        period = ''

        if 'period' in request.QUERY_PARAMS:
            period = request.QUERY_PARAMS['period']

        if not period:
            qry = models.Podcast.objects.raw(
                'SELECT DISTINCT ON ("id", "title") * '
                'FROM ('
                '  SELECT "snotes20_podcast".*'
                '  FROM "snotes20_podcast"'
                '  INNER JOIN "snotes20_episode" ON ("snotes20_podcast"."id" = "snotes20_episode"."podcast_id")'
                '  INNER JOIN "snotes20_publication" ON ("snotes20_episode"."id" = "snotes20_publication"."episode_id")'
                '  WHERE "snotes20_publication"."id" IS NOT NULL'
                ') AS subb '
                'ORDER BY title, id;'
            )
        else:
            qry = models.Podcast.objects.raw(
                'SELECT DISTINCT ON ("id", "title") * '
                'FROM ('
                '  SELECT "snotes20_podcast".*'
                '  FROM "snotes20_podcast"'
                '  INNER JOIN "snotes20_episode" ON ("snotes20_podcast"."id" = "snotes20_episode"."podcast_id")'
                '  INNER JOIN "snotes20_publication" ON ("snotes20_episode"."id" = "snotes20_publication"."episode_id")'
                '  WHERE concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date)) = \'' + str(period) + '\' '
                ') AS subb '
                'ORDER BY title, id;'
            )

        data = serializers.MinimalPodcastSerializer(qry, many=True).data

        return Response(data)