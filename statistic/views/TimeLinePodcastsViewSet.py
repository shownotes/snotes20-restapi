
from rest_framework import viewsets
from rest_framework.response import Response


class TimeLinePodcastsViewSet(viewsets.ViewSet):
    """
    For retrieving number of podcasts per period range (month).
    The last 10 months are returned in descending order.
    ---
    """
    def list(self, request):

        from django.db import connection
        cursor = connection.cursor()##

        # Data retrieval operation - no commit required
        cursor.execute(
                'SELECT * '
                'FROM ( '
                ' SELECT COUNT(DISTINCT "snotes20_podcast"."id"), concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date))'
                '  FROM "snotes20_podcast"'
                '  INNER JOIN "snotes20_episode" ON ("snotes20_podcast"."id" = "snotes20_episode"."podcast_id")'
                '  INNER JOIN "snotes20_publication" ON ("snotes20_episode"."id" = "snotes20_publication"."episode_id")'
                '  WHERE "snotes20_publication"."create_date" IS NOT NULL'
                '  GROUP BY concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date)) '
                '  ORDER BY concat(date_part(\'month\', "snotes20_episode".create_date), \'-\', date_part(\'year\', "snotes20_episode".create_date)) DESC '
                ') AS subb '
                'LIMIT 10; '

        )
        return Response(cursor.fetchall())
