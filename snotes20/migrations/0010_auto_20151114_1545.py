# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0009_auto_20151114_1134'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notifylist',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='notifylist',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='notifylist',
            name='type',
        ),
        migrations.RemoveField(
            model_name='notifylist',
            name='user',
        ),
        migrations.DeleteModel(
            name='Notifylist',
        ),
    ]
