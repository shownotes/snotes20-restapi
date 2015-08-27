from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, Field

from snotes20.models import Document, DocumentMeta, ChatMessage, ChatMessageIssuer, CHAT_MSG_ISSUER_USER
from snotes20.serializers import EpisodeSerializer, PodcastSerializer


class DocumentMetaSerializer(ModelSerializer):
    def __init__(self, *kargs, **kwargs):
        super(DocumentMetaSerializer, self).__init__(*kargs, **kwargs)

    def field_to_native(self, obj, field_name):
        data = super(DocumentMetaSerializer, self).field_to_native(obj, field_name)

        try:
            meta = obj.meta
        except DocumentMeta.DoesNotExist:
            meta = None

        if meta is not None:
            data['shownoters'] = [{'name': shownoter.shown_name()} for shownoter in meta.shownoters.all()]
            data['podcasters'] = [{'name': rpodcaster.name} for rpodcaster in meta.podcasters.all()]

        return data

    class Meta:
        model = DocumentMeta
        fields = ('podcasters',)
        depth = 1


class SubEpisodeSerializer(EpisodeSerializer):
    class Meta(EpisodeSerializer.Meta):
        fields = list(set(EpisodeSerializer.Meta.fields) - {'document', 'creator'})


class DocumentSerializer(ModelSerializer):
    episode = SubEpisodeSerializer()
    meta = DocumentMetaSerializer()
    urlname = Field()

    class Meta:
        model = Document
        fields = ('name', 'editor', 'create_date', 'episode', 'meta', 'urlname')


class ChatMessageIssuerSerializer(ModelSerializer):

    def field_to_native(self, obj, field_name):
        data = super(ChatMessageIssuerSerializer, self).field_to_native(obj, field_name)

        if obj.issuer.type == CHAT_MSG_ISSUER_USER:
            data['name'] = obj.issuer.user.username
            data['color'] = obj.issuer.user.color
        else:
            raise Exception()

        return data

    class Meta:
        model = ChatMessageIssuer
        fields = ('type',)


class ChatMessageSerializer(ModelSerializer):
    issuer = ChatMessageIssuerSerializer()

    class Meta:
        model = ChatMessage
        fields = ('order', 'message', 'date', 'issuer', 'document')
