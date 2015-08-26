# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0007_auto_20141125_1737'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nuser',
            old_name='old_password',
            new_name='showpad_password',
        )
    ]
