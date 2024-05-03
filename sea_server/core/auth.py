# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import secrets

from typing import Callable

from django.contrib.auth.hashers import (
    make_password,
    check_password,
)


def generate_token() -> str:
    return secrets.token_urlsafe(45)


def hash_raw_credentials(raw_credentials: str) -> str:
    return make_password(raw_credentials)


def verify_raw_credentials(raw_credentials: str, hashed_credentials: str, on_rehash: Callable[[str], None]) -> bool:
    return check_password(
        password=raw_credentials,
        encoded=hashed_credentials,
        setter=on_rehash,
    )
