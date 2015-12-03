from django.db import models

# Create your models here.
from snotes20.models import Episode


class WordFrequency(models.Model):
    word = models.CharField(max_length=400, blank=False, null=False)
    frequency = models.IntegerField(blank=False,null=False)
    episode = models.ForeignKey(Episode, related_name="Episodes", blank=False, null=False)

    def __str__(self):
        return "{} ({})".format(self.word, self.frequency)

    class Meta:
        unique_together=('word','episode')
