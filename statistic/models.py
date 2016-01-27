from django.db import models

# Create your models here.
from snotes20.models import Episode, Publication, DocumentState, Podcast


class WordFrequency(models.Model):
    word = models.CharField(max_length=400, blank=False, null=False)
    frequency = models.IntegerField(blank=False,null=False)
    relativ_frequency = models.FloatField(blank=False,null=False)
    episode = models.ForeignKey(Episode, related_name="Wordfrequency_Episodes", blank=False, null=False)
    podcast = models.ForeignKey(Podcast, related_name="Wordfrequency_Podcasts", blank=False, null=False)
    state = models.ForeignKey(DocumentState, related_name="Wordfrequency_DocumentState", blank=False, null=False)

    def __str__(self):
        return "{}".format(self.word)

    class Meta:
        unique_together=('word','episode')


class SignificantPodcastWords(models.Model):
    word = models.CharField(max_length=400, blank=False, null=False)
    significance = models.FloatField(blank=False,null=False)
    podcast = models.ForeignKey(Podcast, related_name="Significant_Podcast_Words", blank=False, null=False)

    def __str__(self):
        return "{}".format(self.word)

    class Meta:
        unique_together=('word','podcast')


class PodcastCosineSimilarity(models.Model):
    podcastx = models.ForeignKey(Podcast, related_name="Cosine_Podcast_x", blank=False, null=False)
    podcasty = models.ForeignKey(Podcast, related_name="Cosine_Podcast_y", blank=False, null=False)
    cosine_sim = models.FloatField(blank=False,null=False)

    def __str__(self):
        return "{}<->{}".format(self.podcastx, self.podcasty)

    class Meta:
        unique_together=('podcastx','podcasty')