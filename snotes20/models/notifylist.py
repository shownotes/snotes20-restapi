from django.db import models

# Create your models here.
from shownotes import settings
from snotes20.models import NUser, NUserSocialType
from datetime import datetime


class Notifylist(models.Model):
    user = models.ForeignKey(NUser, db_index=True, null=False, blank=False, related_name="notify")
    type = models.ForeignKey(NUserSocialType, db_index=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    create_date = models.DateTimeField(default=datetime.now)

    class Meta:
        unique_together = ('user', 'type')
        verbose_name = "Notify"

    def __str__(self):
        return self.user.username + " (" + self.type.human_name + ")"