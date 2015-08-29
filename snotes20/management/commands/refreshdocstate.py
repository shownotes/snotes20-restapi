import logging
import datetime
import time

from django.core.management.base import BaseCommand
from django.db import transaction

import snotes20.models as models
import snotes20.contenttypes as contenttypes


logger = logging.getLogger(__name__)


def update_document(doc, sigh):
    # execute parser
    prepped = contenttypes.prep_state(doc)

    #TODO reduce write access on contenttypes.get_state
    # Two states - sight and live
    with transaction.atomic():
        raw_state, state = contenttypes.get_state(prepped)

        raw_state.save()
        state.save()

        _delete_old_states(doc)
        _save_new_state_to_doc(doc, raw_state, state)

        if sigh:
            pub = models.Publication()
            _save_state_to_publication(pub, doc.episode, raw_state, state)

def _delete_old_states(doc):
    if doc.state:
        try:
            if doc.state.publication:
                doc.state.clear()
        except models.Publication.DoesNotExist:
            doc.state.delete()

    if doc.raw_state:
        try:
            if doc.raw_state.publication_raw:
                doc.raw_state.clear()
        except models.Publication.DoesNotExist:
            doc.raw_state.delete()

def _save_new_state_to_doc(doc, raw_state, state):
    doc.raw_state = raw_state
    doc.state = state
    doc.save()

def _save_state_to_publication(pub, episode, raw_state, state):
    pub.raw_state = raw_state
    pub.state = state
    pub.creator = models.NUser.objects.get(pk=1)
    pub.preliminary = True
    pub.create_date = datetime.datetime(2000, 1, 1)
    pub.episode = episode
    pub.save()

def update_documents(docs, sigh):
    start_time = datetime.datetime.now()

    for doc in docs:
        logger.debug("Updating document:" + doc.name)
        update_document(doc, sigh)

    duration = datetime.datetime.now() - start_time

    logger.debug("took {}s".format(duration.total_seconds()))


class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        mode = 'continuous'

        if len(args) == 1:
            mode = args[0]

        sigh = False

        if mode == 'sighall':
            mode = 'all'
            sigh = True

        if mode == 'continuous':
            while True:
                today = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                docs = models.Document.objects.all().filter(edit_date__gt=today)
                update_documents(docs, sigh)
                time.sleep(1)
        elif mode == 'all':
            docs = models.Document.objects.all()
            update_documents(docs, sigh)
