# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0008_auto_20150827_1159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifylist',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('type', models.ForeignKey(to='snotes20.NUserSocialType')),
                ('user', models.ForeignKey(related_name='notify', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notify',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='notifylist',
            unique_together=set([('user', 'type')]),
        ),
    ]
