# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def migrate_doc_meta_to_doc(apps, schema_editor):
    Document = apps.get_model("snotes20", "Document")

    for doc in Document.objects.all():

        for podcaster in doc.meta.podcasters.all():
            podcaster.document = doc
            podcaster.meta = None
            podcaster.save()

        for shownoter in doc.meta.shownoters.all():
            shownoter.document = doc
            shownoter.metas.clear()
            shownoter.save()

        doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('snotes20', '0007_auto_20141125_1737'),
    ]

    operations = [
        # add former DocumentMeta-Attributes to Document
        migrations.AddField(
            model_name='document',
            name='shownoters',
            field=models.ManyToManyField(to='snotes20.Shownoter', blank=True),
            preserve_default=True,
        ),

        migrations.AddField(
            model_name='rawpodcaster',
            name='document',
            field=models.ForeignKey(to='snotes20.Document', default=0, related_name='podcasters'),
            preserve_default=False,
        ),

        # migrate data from DocumentMeta to Document
        migrations.RunPython(migrate_doc_meta_to_doc),

        # remove ties to DocumentMeta
        migrations.RemoveField(
            model_name='document',
            name='meta',
        ),
        migrations.RemoveField(
            model_name='rawpodcaster',
            name='meta',
        ),

        # delete DocumentMeta
        migrations.DeleteModel(
            name='DocumentMeta',
        ),
    ]
