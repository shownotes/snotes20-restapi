from datetime import datetime

from django.db import models

# Create your models here.
from django_extensions.db.fields import PostgreSQLUUIDField

from snotes20.models import Publication, Podcast


class WordFrequency(models.Model):
    word = models.CharField(max_length=40, blank=False, null=False, unique=True)
    count = models.IntegerField(blank=False,null=False)
    publication = models.ForeignKey(Publication, related_name="publications", blank=False, null=False)

    def __str__(self):
        return "{}".format(self.episode)

    class Meta:
        unique_together=('word','publication')
