import operator

from django.conf import settings
from django.db.models import Q
from functools import reduce
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route

import snotes20.models as models
import snotes20.serializers as serializers

class ArchiveViewSet(viewsets.ViewSet):
    def list(self, request):
        type = 'all'

        if 'type' in request.QUERY_PARAMS:
            type = request.QUERY_PARAMS['type']

        if type == 'recent':
            qry = models.Podcast.objects.raw(
                'SELECT DISTINCT ON ("id", pub_create) * '
                'FROM ('
                '  SELECT "snotes20_podcast".*, snotes20_publication.create_date AS pub_create'
                '  FROM "snotes20_podcast"'
                '  INNER JOIN "snotes20_episode" ON ("snotes20_podcast"."id" = "snotes20_episode"."podcast_id")'
                '  INNER JOIN "snotes20_publication" ON ("snotes20_episode"."id" = "snotes20_publication"."episode_id")'
                '  WHERE "snotes20_publication"."id" IS NOT NULL'
                ') AS subb '
                'ORDER BY pub_create DESC '
                'LIMIT ' + str(settings.ARCHIVE_RECENT_COUNT) + ';'
            )
        elif type == 'full':
            qry = models.Podcast.objects.all()
        else:
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

        data = serializers.MinimalPodcastSerializer(qry, many=True).data

        return Response(data)

    @list_route(methods=['POST'])
    def search(self, request):
        words = request.DATA['words']
        print(words)
        search_argument_list_title = []
        search_argument_list_url = []
        for word in words:
            search_argument_list_title.append(Q(**{'title__icontains': word}))
            search_argument_list_url.append(Q(**{'url__icontains': word}))

        print(reduce(operator.and_, search_argument_list_title))
        print(reduce(operator.and_, search_argument_list_url))
        lines = models.OSFNote.objects.filter(Q(reduce(operator.and_, search_argument_list_title)) | Q(reduce(operator.and_, search_argument_list_url)))\
            .filter(state__publication__isnull=False)\
            .distinct('state__publication__episode')

        # --UPDATE-- here's an args example for completeness
        # order = ['publish_date','title'] #create a list, possibly from GET or POST data
        # ordered_query = query.order_by(*orders()) # Yay, you're ordered now!
        # https://stackoverflow.com/questions/8510057/constructing-django-filter-queries-dynamically-with-args-and-kwargs

        # reduce results (pagination possible)
        #lines = lines[:15]

        for l in lines:
            print(l.title, l.url)

        data = [
            {
                'note': serializers.OSFNoteSerializer(line).data,
                'episode': serializers.EpisodeSerializer(line.state.publication.episode).data,
            } for line in lines
        ]

        return Response(data)
