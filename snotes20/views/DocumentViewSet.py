from datetime import datetime
import time
import string

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Count
from django.core.validators import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action, list_route, detail_route
from django.core.cache import cache

import snotes20.serializers as serializers
import snotes20.models as models
import snotes20.editors as editors
import snotes20.contenttypes as contenttypes


def find_doc_name(prefix, sep='-'):
    if not models.Document.objects.filter(name=prefix).exists():
        return prefix

    for letter in range(1, 26):
        name = prefix + sep + letter
        if not models.Document.objects.filter(name=name).exists():
            return name
    raise Exception()


def create_doc_from_episode(request, episode_pk, number):
    if episode_pk is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    episode = get_object_or_404(models.Episode, pk=episode_pk)
    episode.number = number

    today = datetime.now()

    doc = models.Document()

    doc.name = episode.podcast.slug + '-'

    if episode.number is not None:
        doc.name += episode.number
    else:
        doc.name += today.strftime('%Y-%m-%d')
        doc.name = find_doc_name(doc.name)

    doc.editor = models.EDITOR_ETHERPAD
    doc.creator = request.user

    meta = models.DocumentMeta()

    with transaction.atomic():
        meta.save()
        doc.meta = meta

        doc.save()

        episode.document = doc
        episode.save()

    return Response({'name': doc.name}, status=status.HTTP_201_CREATED)


def create_doc_from_nolive(request):
    if 'podcast' not in request.DATA or 'number' not in request.DATA:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    number = request.DATA['number']

    podcast = get_object_or_404(models.Podcast, pk=request.DATA['podcast'])

    with transaction.atomic():
        episode = models.Episode(
            podcast=podcast,
            creator=request.user,
            type=models.TYPE_PODCAST
        )

        episode.save()

        return create_doc_from_episode(request, episode.pk, number)


def get_doc_impl(document):
    if document is not None:
        data = serializers.DocumentSerializer(instance=document).data
        return document, Response(data)
    else:
        return None, Response(None, status=status.HTTP_404_NOT_FOUND)


def get_doc_by_episode(request, pk=None):
    number = request.QUERY_PARAMS['number']
    podcast = request.QUERY_PARAMS['podcast']

    episode = get_object_or_404(models.Episode, number=number, podcast__slugs__slug=podcast)

    return get_doc_impl(episode.document)


def get_doc(request, pk=None):
    return get_doc_impl(get_object_or_404(models.Document, pk=pk))


class DocumentViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        type = request.QUERY_PARAMS.get('type')

        if not request.user.is_authenticated():
            raise PermissionDenied()

        if type == 'fromepisode':
            return create_doc_from_episode(request, request.DATA.get('episode', None), request.DATA.get('number', None))
        elif type == 'nonlive':
            return create_doc_from_nolive(request)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        type = request.QUERY_PARAMS.get('type')
        mode = 'view'
        if 'edit' in request.QUERY_PARAMS and request.QUERY_PARAMS['edit'] == 'true':
            mode = 'edit'

        if type == 'byepisode':
            doc, resp = get_doc_by_episode(request)
        else:
            doc, resp = get_doc(request, pk)

        if mode == 'edit' and not request.user.has_perm('o_edit_document', doc):
            raise PermissionDenied()
        elif mode == 'view' and not request.user.has_perm('o_view_document', doc):
            raise PermissionDenied()

        if resp.status_code == 200 and request.user.is_authenticated() and 'edit' in request.QUERY_PARAMS:
            editor = editors.EditorFactory.get_editor(doc.editor)
            session_id = editor.generate_session(doc, request.user)
            resp.set_cookie('sessionID', session_id)

            doc.edit_date = datetime.now()

        doc.access_date = datetime.now()
        doc.save(update_fields=['edit_date', 'access_date'])

        return resp

    @action(methods=['POST', 'DELETE'])
    def contributed(self, request, pk=None):
        document = get_object_or_404(models.Document, pk=pk)
        exists = document.meta.shownoters.filter(user=request.user).exists()

        if request.method == 'POST' and not exists:
            shownoter = models.Shownoter(user=request.user)
            shownoter.save()
            document.meta.shownoters.add(shownoter)
        elif request.method == 'DELETE' and exists:
            document.meta.shownoters.filter(user=request.user).delete()

        return Response(status=status.HTTP_202_ACCEPTED)

    @action(methods=['POST'])
    def number(self, request, pk=None):
        document = get_object_or_404(models.Document, pk=pk)

        if not hasattr(document, 'episode'):
            return Response(status=status.HTTP_404_NOT_FOUND)

        episode = document.episode

        if episode.number is not None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            episode.number = int(request.DATA['number'])
            episode.full_clean()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        episode.save()

        return Response(status=status.HTTP_202_ACCEPTED)

    @list_route()
    def todo(self, request):
        if not request.user.has_perm('snotes20.publish_episode') and not models.Podcast.objects.filter(mums=request.user).exists():
            raise PermissionDenied()

        qry = models.Document.objects.filter(episode__isnull=False)\
                                     .annotate(Count('episode__publications'))\
                                     .annotate(Count('episode__publicationrequests'))\
                                     .filter(Q(episode__publications__count=0) |
                                             Q(episode__publicationrequests__count__gt=0))

        if 'search' in request.QUERY_PARAMS:
            key = request.QUERY_PARAMS['search']
            qry = qry.filter(episode__podcast__title__icontains=key)

        return Response({
            'data': serializers.DocumentSerializer(qry[:15], many=True).data,
            'count': qry.count()
        })

    @action(methods=['POST', 'DELETE'])
    def shownoters(self, request, pk=None):
        if 'name' not in request.DATA and 'id' not in request.DATA:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        document = get_object_or_404(models.Document, pk=pk)

        if not hasattr(document, 'episode'):
            return Response(status=status.HTTP_404_NOT_FOUND)

        episode = document.episode

        if not request.user.has_perm('o_publish_episode', episode):
            raise PermissionDenied()

        user = None

        try:
            if 'name' in request.DATA:
                user = models.NUser.objects.get(username=request.DATA['name'])
            else:
                user = models.NUser.objects.get(id=request.DATA['id'])
        except models.NUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            document.meta.shownoters.filter(user=user).delete()
        elif request.method == 'POST':
            shownoter = models.Shownoter(user=user)
            shownoter.save()
            document.meta.shownoters.add(shownoter)

        return Response(status=status.HTTP_202_ACCEPTED)

    @action(methods=['POST', 'DELETE'])
    def podcasters(self, request, pk=None):
        if 'name' not in request.DATA:
            raise PermissionDenied()

        name = request.DATA['name']
        document = get_object_or_404(models.Document, pk=pk)
        exists = any(rpodcaster.name == name for rpodcaster in document.meta.podcasters.all())

        if request.method == 'POST' and not exists:
            rpodcaster = models.RawPodcaster(name=name, meta=document.meta)
            try:
                rpodcaster.clean_fields()
            except ValidationError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            document.meta.podcasters.add(rpodcaster)
        elif request.method == 'DELETE' and exists:
            document.meta.podcasters.get(name=name).delete()

        return Response(status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['POST', 'GET'], permission_classes=(AllowAny,))
    def text(self, request, pk=None):
        document = get_object_or_404(models.Document, pk=pk)
        source = document

        type = 'osf'

        if 'type' in request.QUERY_PARAMS:
            type = request.QUERY_PARAMS['type']

        if 'pub' in request.QUERY_PARAMS:
            pub = request.QUERY_PARAMS['pub']
        else:
            pub = None

        cache_key = 'doctext_' + document.name

        if pub is not None:
            cache_key += '_' + pub

        data = cache.get(cache_key)

        if data is None:
            if pub is not None:
                if pub == 'newest':
                    source = document.episode.publications.order_by('create_date')[:1][0]
                else:
                    try:
                        num = int(pub)
                        source = document.episode.publications.order_by('create_date')[num:num + 1][0]
                    except IndexError:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                    except ValueError:
                        return Response(status=status.HTTP_400_BAD_REQUEST)

            if type == 'json':
                try:
                    data = source.state.osfdocumentstate.to_dict()
                except models.OSFDocumentState.DoesNotExist:
                    return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
            elif type == 'raw':
                data  = source.raw_state.text
            elif type == 'osf':
                data = None
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            cache.set(cache_key, data, 1)

        response = Response({'data': data}, status=status.HTTP_200_OK)
        return response

    @action(methods=['GET'])
    def errors(self, request, pk=None):
        document = get_object_or_404(models.Document, pk=pk)
        errors = document.state.errors.all()
        data = serializers.DocumentStateErrorSerializer(errors, many=True).data
        return Response(data, status=status.HTTP_200_OK)


    @action(methods=['POST', 'GET'])
    def publications(self, request, pk=None):
        document = get_object_or_404(models.Document, pk=pk)

        if not hasattr(document, 'episode'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        episode = document.episode

        if request.method == 'POST':
            if not request.user.is_authenticated() or not request.user.has_perm('o_publish_episode', episode):
                return Response(status=status.HTTP_403_FORBIDDEN)

            podcasters = request.DATA['podcasters']
            request.DATA['podcasters'] = []

            cover = None
            if 'cover' in request.DATA:
                cover = request.DATA['cover']
                del request.DATA['cover']

            request.DATA['create_date'] = datetime.now()

            serialized = serializers.PublicationSerializer(data=request.DATA)

            if not serialized.is_valid():
                return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)

            pub = serialized.object

            prepped = contenttypes.prep_state(document)

            with transaction.atomic():
                raw_state, state = contenttypes.get_state(prepped)
                state.save()

                if cover is not None:
                    if cover['id'] == 'new':
                        cover = models.Cover.from_url(request.user, cover['file'])
                    else:
                        cover = models.Cover.objects.get(pk=cover['id'])

                    episode.cover = cover
                    episode.save()

                pub.creator = request.user
                pub.state = state
                pub.raw_state = raw_state
                pub.episode = episode

                pub.save()

                pub.shownoters.add(*document.meta.shownoters.all())

                episode.publicationrequests.all().delete()

            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'GET':
            return Response(episode.publications)

    @action(methods=['POST'])
    def publicationrequests(self, request, pk=None):
        document = get_object_or_404(models.Document, pk=pk)

        if not hasattr(document, 'episode'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        episode = document.episode

        if episode.publicationrequests.count() != 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        comment = ""

        if 'comment' in request.DATA:
            comment = request.DATA['comment']

        request = models.PublicationRequest(episode=episode,
                                            comment=comment,
                                            requester=request.user,
                                            create_date=datetime.now())
        try:
            request.clean_fields()
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request.save()

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['GET'])
    def canpublish(self, request, pk=None):
        document = get_object_or_404(models.Document, pk=pk)

        if not hasattr(document, 'episode'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        episode = document.episode

        if not request.user.is_authenticated() or not request.user.has_perm('o_publish_episode', episode):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_200_OK)

    #def list(self, request):
    #    pass

    #def update(self, request, pk=None):
    #    pass

    #def partial_update(self, request, pk=None):
    #    pass

    #def destroy(self, request, pk=None):
    #    pass