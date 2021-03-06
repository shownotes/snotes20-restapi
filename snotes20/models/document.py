from datetime import datetime

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_delete
from django_extensions.db.fields import PostgreSQLUUIDField

from .showoter import Shownoter
import snotes20.editors as editors

from shownotes.settings import SITEURL

EDITOR_ETHERPAD  = 'EP'

EDITOR_CHOICES = (
    (EDITOR_ETHERPAD, 'Etherpad'),
)

CONTENTTYPE_OSF  = 'OSF'
CONTENTTYPE_TXT  = 'TXT'

CONTENTTYPE_CHOICES = (
    (CONTENTTYPE_OSF, 'OSF'),
    (CONTENTTYPE_TXT, 'Text'),
)


class DocumentState(models.Model):
    id = PostgreSQLUUIDField(primary_key=True, auto=True)
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.id


class DocumentStateError(models.Model):
    state = models.ForeignKey(DocumentState, related_name="errors")
    line = models.PositiveIntegerField()
    message = models.CharField(max_length=400)

    def get_absolute_url(self):
        doc = Document.objects.get(state=self.state)
        return SITEURL+'/doc/'+doc.name+'/edit/'

class TextDocumentState(DocumentState):
    text = models.TextField()

    def to_osf_str(self):
        return self.text

    def __str__(self):
        return "OSFDocumentState, " + str(len(self.text)) + " chars"


class DocumentMeta(models.Model):
    id = PostgreSQLUUIDField(primary_key=True, auto=True)
    shownoters = models.ManyToManyField(Shownoter, blank=True)

    def __str__(self):
        try:
            return "Meta for " + self.document.__str__()
        except:
            return "Meta without document?"


class RawPodcaster(models.Model):
    meta = models.ForeignKey(DocumentMeta, related_name="podcasters")
    name = models.CharField(max_length=150, validators=[MinLengthValidator(2)])


class Document(models.Model):
    name = models.CharField(primary_key=True, max_length=40)
    state = models.ForeignKey(DocumentState, null=True, blank=True, on_delete=models.SET_NULL)
    raw_state = models.ForeignKey(TextDocumentState, null=True, blank=True, on_delete=models.SET_NULL, related_name="rdocument")
    editor = models.CharField(max_length=3, choices=EDITOR_CHOICES)
    create_date = models.DateTimeField(default=datetime.now)
    access_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    meta = models.OneToOneField(DocumentMeta, related_name='document', null=True, blank=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=CONTENTTYPE_CHOICES, default=CONTENTTYPE_OSF)
    access_time = models.DateTimeField(null=True, blank=True)

    def urlname(self):
        editor = editors.EditorFactory.get_editor(self.editor)
        urlname = editor.get_urlname_for_document(self)
        return urlname

    def __str__(self):
        return "{}".format(self.name)

    def get_absolute_url(self, instance):
        # Improve to none static doc
        return SITEURL+'/doc/'+instance.name+'/edit/'

@receiver(post_delete, sender=Document)
def doc_post_delete_meta(sender, instance, *args, **kwargs):
    if instance.meta:
        instance.meta.delete()


CHAT_MSG_ISSUER_USER = 'USR'

CHAT_MSG_ISSUER_CHOICES = (
    (CHAT_MSG_ISSUER_USER, 'User'),
)


class ChatMessageIssuer(models.Model):
    type = models.CharField(max_length=3, choices=CHAT_MSG_ISSUER_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return "{}".format(self.user.username)


class ChatMessage(models.Model):
    id = PostgreSQLUUIDField(primary_key=True, auto=True)
    order = models.BigIntegerField()
    document = models.ForeignKey(Document, related_name='messages')
    issuer = models.OneToOneField(ChatMessageIssuer)
    message = models.CharField(max_length=200)
    date = models.DateTimeField(default=datetime.now)
