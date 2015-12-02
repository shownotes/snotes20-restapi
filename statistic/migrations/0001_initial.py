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
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('word', models.CharField(unique=True, max_length=40)),
                ('count', models.IntegerField()),
                ('publication', models.ForeignKey(related_name='publications', to='snotes20.Publication')),
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
