from django.contrib import admin

# Register your models here.
from statistic import models
from django.contrib import admin


@admin.register(models.WordFrequency)
class WordfrequencyAdmin(admin.ModelAdmin):
    fields = ('word', 'frequency', 'episode')
    list_display = ('word', 'frequency', 'episode')
    list_filter = ('word', 'frequency', 'episode')


@admin.register(models.SignificantPodcastWords)
class SignificantPodcastWordAdmin(admin.ModelAdmin):
    fields = ('word', 'significance', 'podcast')
    list_display = ('word', 'significance', 'podcast')
    list_filter = ('word', 'significance', 'podcast')


@admin.register(models.PodcastCosineSimilarity)
class PodcastCosineSimilarityAdmin(admin.ModelAdmin):
    fields = ('podcastx', 'podcasty', 'cosine_sim')
    list_display = ('podcastx', 'podcasty', 'cosine_sim')
    list_filter = ('podcastx', 'podcasty')