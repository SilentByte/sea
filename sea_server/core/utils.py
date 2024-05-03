# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


def truncate_ellipsis(text: str, max_length: int, ending: str = '...') -> str:
    if len(text) <= max_length:
        return text
    else:
        return text[:max_length - len(ending)] + '...'
