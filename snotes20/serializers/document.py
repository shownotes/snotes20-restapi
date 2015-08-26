from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, Field

from snotes20.models import Document, ChatMessage, ChatMessageIssuer, CHAT_MSG_ISSUER_USER
from snotes20.serializers import EpisodeSerializer, PodcastSerializer


class SubEpisodeSerializer(EpisodeSerializer):
    class Meta(EpisodeSerializer.Meta):
        fields = list(set(EpisodeSerializer.Meta.fields) - {'document',})


class DocumentSerializer(ModelSerializer):
    episode = SubEpisodeSerializer()
    urlname = Field()

    def to_native(self, obj):
        data = super(DocumentSerializer, self).to_native(obj)

        data['shownoters'] = [{'name': shownoter.shown_name()} for shownoter in obj.shownoters.all()]
        data['podcasters'] = [{'name': rpodcaster.name} for rpodcaster in obj.podcasters.all()]

        return data

    class Meta:
        model = Document
        fields = ('name', 'editor', 'create_date', 'episode', 'urlname')


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
