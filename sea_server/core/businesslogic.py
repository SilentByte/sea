# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


import logging
import hashlib
import os.path
import re

import pytz

from glob import glob
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from sea.config import SeaConfig
from sea.inference import (
    SeaInferenceClient,
    InferenceInteraction,
    InferenceResult,
)

from server import settings

from core import auth
from core.models import (
    Document,
    InferenceLog,
    UserAccount,
    AuthToken,
)

log = logging.getLogger(__name__)


def file_sha256(file_name: str) -> str:
    with open(file_name, 'rb', buffering=0) as fp:
        return hashlib.file_digest(fp, 'sha256').hexdigest()


def rehash_user_credentials(user: UserAccount, raw_credentials: str) -> None:
    user.hashed_credentials = auth.hash_raw_credentials(raw_credentials)
    user.save()


def verify_credentials(user: UserAccount, raw_credentials: str) -> bool:
    return auth.verify_raw_credentials(
        raw_credentials=raw_credentials,
        hashed_credentials=user.hashed_credentials,
        on_rehash=lambda rc: rehash_user_credentials(user, rc),
    )


def create_auth_token(
        user: UserAccount,
        device_name: str | None = None,
        expires_on: datetime | None = None,
) -> AuthToken:
    if expires_on is None:
        expires_on = timezone.now() + timedelta(days=30 * 6)

    return AuthToken.objects.create(
        user=user,
        token=auth.generate_token(),
        device_name=device_name or '',
        expires_on=expires_on,
    )


def authenticate_with_credentials(email: str, raw_credentials: str) -> tuple[UserAccount, AuthToken] | None:
    with transaction.atomic():
        user: UserAccount = UserAccount.objects \
            .select_for_update() \
            .filter(email=email) \
            .first()

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_credentials(user, raw_credentials):
            return None

        return user, create_auth_token(
            user=user,
            expires_on=timezone.now() + timedelta(days=90),
        )


def authenticate_with_token(token: str) -> UserAccount | None:
    now = timezone.now()

    auth_token: AuthToken = AuthToken.objects \
        .select_related('user') \
        .filter(token=token, expires_on__gt=now) \
        .first()

    if auth_token is None:
        return None

    auth_token.last_auth_on = now
    auth_token.save(update_fields=['last_auth_on'])

    return auth_token.user


def extract_document_search_tags(file_name: str) -> list[str]:
    file_name = Path(file_name).stem.lower()
    return list(set(re.split(r'[\s\-_.]+', file_name)))


def synchronize_documents() -> None:
    document_file_names = glob(os.path.join(settings.DOCUMENT_DIR, '**/*.pdf'), recursive=True)

    with transaction.atomic():
        for i, file_name in enumerate(sorted(document_file_names), 1):
            file_hash = file_sha256(file_name)

            log.info('Synchronizing document %s/%s %s %s', i, len(document_file_names), file_hash, file_name)

            Document.objects.update_or_create(
                file_hash=file_hash,
                defaults={
                    'file_name': file_name,
                    'file_creation_ts': datetime.fromtimestamp(os.path.getctime(file_name), tz=pytz.UTC),
                    'file_modification_ts': datetime.fromtimestamp(os.path.getmtime(file_name), tz=pytz.UTC),
                    'search_tags': extract_document_search_tags(file_name),
                    'last_checked_on': timezone.now(),
                },
                create_defaults={
                    'file_name': file_name,
                    'file_hash': file_hash,
                    'file_size': os.path.getsize(file_name),
                    'file_creation_ts': datetime.fromtimestamp(os.path.getctime(file_name), tz=pytz.UTC),
                    'file_modification_ts': datetime.fromtimestamp(os.path.getmtime(file_name), tz=pytz.UTC),
                    'search_tags': extract_document_search_tags(file_name),
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


@dataclass
class DocumentInfo:
    file_name: str
    file_hash: str

    def to_dict(self) -> dict:
        return {
            'file_name': self.file_name,
            'file_hash': self.file_hash,
        }


def search_documents(query: str) -> list[DocumentInfo]:
    query = query.strip()

    if not query:
        return []

    documents = Document.objects.filter(
        Q(file_name=query)
        | Q(file_hash=query.lower())
        | Q(search_tags__overlap=extract_document_search_tags(query))
        | Q(file_name__icontains=query),
    ).order_by('file_name')[:6]

    return [
        DocumentInfo(os.path.basename(d.file_name), d.file_hash)
        for d in documents
    ]


def execute_inference_vector_search(query: str) -> list[DocumentInfo]:
    sea_config = SeaConfig()

    client = SeaInferenceClient(
        vector_search_endpoint=sea_config.vector_search_endpoint,
        vector_search_index=sea_config.document_vectors_index,
        result_count=8,
    )

    return [
        DocumentInfo(s.file_name, s.file_hash)
        for s in client.query_search_index(query)
    ]


def execute_inference_query(user: UserAccount | None, inference_interactions: list[InferenceInteraction]) -> InferenceResult:
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
