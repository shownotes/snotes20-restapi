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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('word', models.CharField(max_length=40, unique=True)),
                ('frequency', models.IntegerField()),
                ('publication', models.ForeignKey(to='snotes20.Publication', related_name='publications')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='wordfrequency',
            unique_together=set([('word', 'publication')]),
        ),
    ]
