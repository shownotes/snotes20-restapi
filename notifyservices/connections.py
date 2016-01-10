import logging

from django.core.serializers import json
from kombu import Exchange, Connection
import json
from django.db.models.signals import post_save
from kombu.message import Message

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


class NoftiyService(object):
    def __init__(self):
        if not settings.NOTIFYSERVICE:
            return

        self.conn = Connection(settings.RABBITMQ_URI)
        self.exchanges = {}
        self.create_bounded_Exchange("Publication")
        post_save.connect(self.publicationrequest, sender=models.PublicationRequest, weak=False, dispatch_uid='publication_request')
        post_save.connect(self.publication, sender=models.Publication, weak=False, dispatch_uid='publication_new')

        # self.create_bounded_Exchange("Document")
        #Zwei Aufrufe von Save - Nachschauen wo
        # created true if exsists
        # raw testen - loaddatacheck
        #post_save.connect(self.newdocument, sender=models.Document,created, weak=False, dispatch_uid='document_new')

    def create_bounded_Exchange(self, exchangename):
        self.exchanges[exchangename] = Exchange(exchangename, 'direct', durable=True, channel=self.conn.default_channel)
        self.exchanges[exchangename].declare()

    def publicationrequest(self, sender, instance, **kwargs):
        pk = str(instance.pk)
        requester = str(instance.requester.username)
        podcast = str(instance.episode.podcast.slug)
        episodenumber = str(instance.episode.number)

        body = {'pk': pk, 'issuer': requester, 'podcast': podcast, 'episodenumber': episodenumber}
        self.publish("Publication", "publication.request", body)

    def publication(self, sender, instance, **kwargs):
        pk = str(instance.pk)
        creator = str(instance.creator.username)
        podcast = str(instance.episode.podcast.slug)
        episodenumber = str(instance.episode.number)

        body = {'pk': pk, 'issuer': creator , 'podcast': podcast, 'episodenumber': episodenumber}
        self.publish("Publication", "publication.new",body)

    def newdocument(self, sender, instance, **kwargs):
        pk = str(instance.pk)
        name = str(instance.name)

        body = {'pk': pk, 'name': name}
        self.publish("Document", "document.new", body)

    def publish(self, exchangename, routing_key, body):
        producer = self.conn.Producer(serializer='json')
        producer.publish(json.dumps(body), exchange=self.exchanges[exchangename], routing_key=routing_key)
        producer.close()