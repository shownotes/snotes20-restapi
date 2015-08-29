from datetime import datetime

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_delete

from django_extensions.db.fields import PostgreSQLUUIDField

from .state import DocumentState, TextDocumentState
from .showoter import Shownoter
import snotes20.editors as editors

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
        try:
            epi = str(self.episode)
        except:
            epi = "no episode"

        return "{}".format(self.name)

@receiver(post_delete, sender=Document)
def doc_post_delete_meta(sender, instance, *args, **kwargs):
    if instance.meta:
        instance.meta.delete()
