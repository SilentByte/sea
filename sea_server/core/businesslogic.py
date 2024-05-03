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
from django.contrib.auth.models import User
from django.db import transaction

from sea.config import SeaConfig
from sea.inference import (
    SeaInferenceClient,
    InferenceInteraction,
    InferenceResult,
)

from server import settings

from core.models import (
    Document,
    InferenceLog,
)

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


def get_document_path(file_hash: str) -> str | None:
    document: Document = Document.objects \
        .filter(file_hash=file_hash) \
        .only('file_name') \
        .first()

    if document is None:
        return None

    return document.file_name


def execute_inference_query(user: User | None, inference_interactions: list[InferenceInteraction]) -> InferenceResult:
    sea_config = SeaConfig()
    client = SeaInferenceClient(
        vector_search_endpoint=sea_config.vector_search_endpoint,
        vector_search_index=sea_config.document_vectors_index,
        result_count=4,
    )

    inference_result = client.infer_interaction(inference_interactions)

    InferenceLog.objects.create(
        user=user,
        input=[ii.to_dict() for ii in inference_interactions],
        output=inference_result.to_dict(),
    )

    return inference_result
