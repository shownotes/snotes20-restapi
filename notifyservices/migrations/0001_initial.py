# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0010_auto_20151114_1545'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifylist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now)),
                ('creator', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
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
