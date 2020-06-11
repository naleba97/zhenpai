import re
from typing import Tuple


def sanitize(word: str):
    return re.sub('[\W_]+', '', word)


def parse_message(message: str):
    return message.content.split(' ')


def create_redis_key(server_id: int, tag_name: str):
    return "server:{server_id}:tag:{tag_name}".format(server_id=server_id, tag_name=tag_name)

