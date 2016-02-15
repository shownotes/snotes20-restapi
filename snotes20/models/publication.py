from django.db import models
from django.conf import settings

from django_extensions.db.fields import PostgreSQLUUIDField

from .showoter import Shownoter
from .podcast import Episode
from .document import DocumentState, TextDocumentState

class Podcaster(models.Model):
    id = PostgreSQLUUIDField(primary_key=True, auto=True)
    uri = models.URLField(unique=True, db_index=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class PubBase(models.Model):
    id = PostgreSQLUUIDField(primary_key=True, auto=True)
    create_date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=250,  blank=True, null=True)

    class Meta:
        abstract = True


class Publication(PubBase):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_publications")
    episode = models.ForeignKey(Episode, related_name="publications")
    shownoters = models.ManyToManyField(Shownoter, blank=True, related_name='contributed_publications')
    podcasters = models.ManyToManyField(Podcaster, blank=True, related_name='contributed_publications')
    preliminary = models.BooleanField(default=False)
    state = models.OneToOneField(DocumentState, related_name="publication")
    raw_state = models.OneToOneField(TextDocumentState, related_name="publication_raw")

    def __str__(self):
        return "{}".format(self.episode)


class PublicationRequest(PubBase):
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requested_publicationrequests')
    episode = models.ForeignKey(Episode, related_name="publicationrequests")
