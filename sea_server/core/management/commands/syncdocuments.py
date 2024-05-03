# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import sys

from django.core.management.base import BaseCommand

from core import businesslogic


def eprint(*args):
    print(*args, file=sys.stderr, flush=True)


class Command(BaseCommand):
    help = 'Synchronizes all documents in the configured folder with the database'

    def handle(self, *args, **options):
        eprint('SYNCHRONIZING ALL DOCUMENTS...')
        businesslogic.synchronize_documents()
