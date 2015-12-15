from django.db import models

# Create your models here.
from snotes20.models import Episode, Publication, DocumentState, Podcast


class WordFrequency(models.Model):
    word = models.CharField(max_length=400, blank=False, null=False)
    frequency = models.IntegerField(blank=False,null=False)
    relativ_frequency = models.FloatField(blank=False,null=False)
    episode = models.ForeignKey(Episode, related_name="Episodes", blank=False, null=False)
    podcast = models.ForeignKey(Podcast, related_name="Podcasts", blank=False, null=False)
    state = models.ForeignKey(DocumentState, related_name="DocumentState", blank=False, null=False)

    def __str__(self):
        return "{}".format(self.word)

    class Meta:
        unique_together=('word','episode')
