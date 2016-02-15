import logging


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from snotes20.models import OSFNote, Document, TextDocumentState, Publication
from shownotes.settings import SITEURL
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = ''
    help = 'Finde broken Documents'

    def handle(self, *args, **options):
        header_notes = TextDocumentState.objects.filter(text__contains='HEADER').values('id')
        pirate_notes = TextDocumentState.objects.filter(text__contains='shownotes.piratenpad.de').values('id')
        documents = Document.objects.filter(Q(raw_state_id__in=header_notes) | Q(raw_state_id__in=pirate_notes))
        for doc in documents:
            if Publication.objects.filter(episode__document=doc).exists():
                print('(Veröffentlicht)\t' + SITEURL+'/doc/'+doc.name)
            else:
                print('\t\t\t'+SITEURL+'/doc/'+doc.name)
