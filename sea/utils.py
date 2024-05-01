# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #

import time
from typing import Any


def dict_item_from_path(dictionary: dict[str, Any], path: str, default: Any = None) -> Any | None:
    item = dictionary

    for segment in path.split('.'):
        item = item.get(segment, None)
        if item is None:
            return default

    return item


def epoch() -> float:
    return time.time()


def sleep(seconds: float) -> None:
    time.sleep(seconds)
