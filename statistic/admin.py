from django.contrib import admin

# Register your models here.
from statistic import models
from django.contrib import admin

@admin.register(models.WordFrequency)
class NotifyList(admin.ModelAdmin):
    fields = ('word', 'frequency', 'episode')
    list_display = ('word', 'frequency', 'episode')
    list_filter = ('word', 'frequency', 'episode')