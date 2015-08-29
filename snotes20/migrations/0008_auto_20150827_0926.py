# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0007_auto_20141125_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publicationrequest',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
