# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0002_auto_20151202_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordfrequency',
            name='episode',
            field=models.ForeignKey(to='snotes20.Episode', related_name='Episodes'),
            preserve_default=True,
        ),
    ]
