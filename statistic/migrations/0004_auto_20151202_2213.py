# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('statistic', '0003_auto_20151202_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordfrequency',
            name='word',
            field=models.CharField(max_length=40),
            preserve_default=True,
        ),
    ]
