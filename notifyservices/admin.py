from django.contrib import admin
from notifyservices import models

@admin.register(models.Notifylist)
class NotifyList(admin.ModelAdmin):
    fields = ('user', 'type','creator', 'create_date')
    list_display = ('__str__', 'creator','create_date')
    list_filter = ('creator','create_date')