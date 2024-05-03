# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


import logging
import hashlib
import os.path

from glob import glob
from datetime import datetime

import pytz
from django.db import transaction

from server import settings
from core.models import Document

log = logging.getLogger(__name__)


def file_sha256(file_name: str) -> str:
    with open(file_name, 'rb', buffering=0) as fp:
        return hashlib.file_digest(fp, 'sha256').hexdigest()


def synchronize_documents() -> None:
    document_file_names = glob(os.path.join(settings.DOCUMENT_DIR, '**/*.pdf'), recursive=True)

    with transaction.atomic():
        for i, file_name in enumerate(sorted(document_file_names), 1):
            file_hash = file_sha256(file_name)

            log.info('Synchronizing document %s/%s %s %s', i, len(document_file_names), file_hash, file_name)

            Document.objects.update_or_create(
                file_hash=file_hash,
                defaults={
                    'file_creation_ts': datetime.fromtimestamp(os.path.getctime(file_name), tz=pytz.UTC),
                    'file_modification_ts': datetime.fromtimestamp(os.path.getmtime(file_name), tz=pytz.UTC),
                },
                create_defaults={
                    'file_name': file_name,
                    'file_hash': file_hash,
                    'file_size': os.path.getsize(file_name),
                    'file_creation_ts': datetime.fromtimestamp(os.path.getctime(file_name), tz=pytz.UTC),
                    'file_modification_ts': datetime.fromtimestamp(os.path.getmtime(file_name), tz=pytz.UTC),
                }
            )
