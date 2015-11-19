import logging

from django.core.serializers import json
from kombu import Exchange, Connection
import json
from django.db.models.signals import post_save

from shownotes import settings
import snotes20.models as models


LOGGER = logging.getLogger(__name__)

#import snotes20.serializers as serializers
# TT_DOCUMENT_NEW = "DOCUMENT_NEW"
# TT_DOCUMENT_CHATMESSAGE = "DOCUMENT_CHATMESSAGE"
# TT_PUBLICATION_NEW = "PUBLICATION_NEW"
# TT_PUBLICATION_REQUESTED = "PUBLICATION_REQUESTED"
# TT_EPISODE_NUMBER_CHANGED = "EPISODE_NUMBER_CHANGED"
# TT_EPISODE_ADDED = "EPISODE_ADDED"
# TT_PODCAST_ADDED = "PODCAST_ADDED"
# TT_USER_NEW = "USER_NEW"
# TT_USER_UPDATED = "USER_UPDATED"

def publication_exchange():
    return Exchange('Publication', 'direct', durable=True)


def document_exchange():
    return Exchange('Document', 'direct', durable=True)



def init():
    if not settings.RABBITMQ_ENABLED:
        return
    post_save.connect(publicationrequest, sender=models.PublicationRequest, weak=False, dispatch_uid='publication_request')
    post_save.connect(publication, sender=models.Publication, weak=False, dispatch_uid='publication_new')
    #Zwei Aufrufe von Save - Nachschauen wo
    #post_save.connect(newdocument, sender=models.Document, weak=False, dispatch_uid='document_new')


def publicationrequest(sender, instance, **kwargs):
    print("publication request")
    pk = str(instance.pk)
    requester = str(instance.requester.username)
    podcast = str(instance.episode.podcast.slug)
    episodenumber = str(instance.episode.number)

    body = {'pk': pk, 'issuer': requester, 'podcast': podcast, 'episodenumber': episodenumber}
    publish(publication_exchange(),"publication.request", json.dumps(body))


def publication(sender, instance, **kwargs):
    pk = str(instance.pk)
    creator = str(instance.creator.username)
    podcast = str(instance.episode.podcast.slug)
    episodenumber = str(instance.episode.number)

    body = {'pk': pk, 'issuer': creator , 'podcast': podcast, 'episodenumber': episodenumber}
    publish(publication_exchange(),"publication.new", json.dumps(body))


def newdocument(sender, instance, **kwargs):
    pk = str(instance.pk)
    name = str(instance.name)

    body = {'pk': pk, 'name': name}
    publish(document_exchange(),"document.new", json.dumps(body))


def publish(exchange, routing_key, body):
    if not settings.RABBITMQ_ENABLED:
        return

    with Connection(settings.RABBITMQ_URI) as conn:
        # produce
        producer = conn.Producer(serializer='json')
        producer.publish(body, exchange=exchange, routing_key=routing_key)
        producer.close()