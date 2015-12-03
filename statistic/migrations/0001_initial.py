# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0010_auto_20151114_1545'),
    ]

    operations = [
        migrations.CreateModel(
            name='WordFrequency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('word', models.CharField(max_length=400)),
                ('frequency', models.IntegerField()),
                ('relativ_frequency', models.FloatField()),
                ('episode', models.ForeignKey(to='snotes20.Episode', related_name='Episodes')),
                ('podcast', models.ForeignKey(to='snotes20.Podcast', related_name='Podcasts')),
                ('state', models.ForeignKey(to='snotes20.DocumentState', related_name='DocumentState')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='wordfrequency',
            unique_together=set([('word', 'episode')]),
        ),
    ]
