# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0010_auto_20151114_1545'),
        ('statistic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignificantPodcastWords',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('word', models.CharField(max_length=400)),
                ('significance', models.FloatField()),
                ('podcast', models.ForeignKey(to='snotes20.Podcast', related_name='Significant_Podcast_Words')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='significantpodcastwords',
            unique_together=set([('word', 'podcast')]),
        ),
        migrations.AlterField(
            model_name='wordfrequency',
            name='episode',
            field=models.ForeignKey(to='snotes20.Episode', related_name='Wordfrequency_Episodes'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wordfrequency',
            name='podcast',
            field=models.ForeignKey(to='snotes20.Podcast', related_name='Wordfrequency_Podcasts'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wordfrequency',
            name='state',
            field=models.ForeignKey(to='snotes20.DocumentState', related_name='Wordfrequency_DocumentState'),
            preserve_default=True,
        ),
    ]
