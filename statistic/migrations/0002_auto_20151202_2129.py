# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wordfrequency',
            old_name='publication',
            new_name='episode',
        ),
        migrations.AlterUniqueTogether(
            name='wordfrequency',
            unique_together=set([('word', 'episode')]),
        ),
    ]
