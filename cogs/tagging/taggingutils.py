import re
from typing import Tuple


def sanitize(word: str):
    return re.sub('[\W_]+', '', word)


def parse_message(message: str):
    return message.content.split(' ')


def create_kv_key(server_id: int, tag_name: str):
    return f"server:{server_id}:tag:{tag_name}"


def get_values_from_kv_key(key: str) -> Tuple[str, str]:
    split = key.split(':')
    return split[1], split[3]
