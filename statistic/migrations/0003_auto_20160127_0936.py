# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0010_auto_20151114_1545'),
        ('statistic', '0002_auto_20160126_2028'),
    ]

    operations = [
        migrations.CreateModel(
            name='PodcastCosineSimilarity',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('cosine_sim', models.FloatField()),
                ('podcastx', models.ForeignKey(to='snotes20.Podcast', related_name='Cosine_Podcast_x')),
                ('podcasty', models.ForeignKey(to='snotes20.Podcast', related_name='Cosine_Podcast_y')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='podcastcosinesimilarity',
            unique_together=set([('podcastx', 'podcasty')]),
        ),
    ]
