# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import secrets


def generate_token() -> str:
    return secrets.token_urlsafe(45)
