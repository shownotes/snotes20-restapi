from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete
from etherpad_lite import EtherpadException
import snotes20.models as models
import snotes20.editors as editors
import snotes20.hereberabbits as rbbits


class DefaultConfig(AppConfig):
    name = 'snotes20'

    def ready(self):
        #import snotes20.serializers as serializers

        #rbbits.add_create_wire(models.Document, rbbits.TT_DOCUMENT_NEW)
        #rbbits.add_create_wire(models.ChatMessage, rbbits.TT_DOCUMENT_CHATMESSAGE, True, serializers.ChatMessageSerializer)
        #rbbits.add_create_wire(models.Publication, rbbits.TT_PUBLICATION_NEW)
        #rbbits.add_create_wire(models.PublicationRequest, rbbits.TT_PUBLICATION_REQUESTED)

        #rbbits.init()

        def editor_create_doc(sender, instance, created, **kwargs):
            if created:
                editor = editors.EditorFactory.get_editor(instance.editor)
                editor.create_document(instance)

        def editor_delete_doc(sender, instance, **kwargs):
            editor = editors.EditorFactory.get_editor(instance.editor)
            try:
                editor.delete_document(instance)
            except EtherpadException as ex:
                if ex.args[0] == 'padID does not exist':
                    pass  # ignore exception of the padID does not exist (already deleted?)
                else:
                    raise  # re-raise all other errors

        post_save.connect(editor_create_doc, sender=models.Document, weak=False, dispatch_uid='editor_create_doc')
        post_delete.connect(editor_delete_doc, sender=models.Document, weak=False, dispatch_uid='editor_delete_doc')
