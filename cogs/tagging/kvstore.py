import abc
import logging
import pickle
import redis
from typing import Dict
from typing import AnyStr
from typing import List
from typing import Tuple

from . import constants


class TaggingItem(object):
    """
    Thing to be retrieved, can be an image file, a gif, a soundbite,
    a url with an embed preview, a youtube link, a text document, etc.
    """
    def __init__(self, url: str = None, local_url: str = None):
        self._url = url
        self._local_url = local_url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def local_url(self):
        return self._local_url

    @local_url.setter
    def local_url(self, value):
        self._local_url = value

    def to_dict(self):
        result = {
            key[1:]: getattr(self, key)
            for key in self.__dict__
            if key[0] == '_' and hasattr(self, key)
        }
        return result

    @classmethod
    def from_dict(cls, data):
        item = cls()
        for attr in ('url', 'local_url'):
            try:
                value = data[attr]
            except KeyError:
                continue
            else:
                setattr(item, '_' + attr, value)
        return item


class BaseKeyValueStore(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        if (cls is subclass and any("__getitem__" in B.__dict__ for B in subclass.__mro__) and
                any("__setitem__" in B.__dict__ for B in subclass.__mro__) and
                any("__contains__" in B.__dict__ for B in subclass.__mro__)):
            return True
        return NotImplemented

    @abc.abstractmethod
    def __getitem__(self, key: str) -> TaggingItem:
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, key: str, value: TaggingItem):
        raise NotImplementedError

    @abc.abstractmethod
    def __contains__(self, key: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, key: str) -> TaggingItem:
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, key: str, value: TaggingItem):
        raise NotImplementedError


class DictKeyValueStore(BaseKeyValueStore):
    def __init__(self):
        self.logger = logging.getLogger('zhenpai.tagging.kvstore')
        self.kvstore: Dict[str, TaggingItem] = {}
        self.load()

    def __getitem__(self, key: str) -> TaggingItem:
        return self.kvstore[key]

    def __setitem__(self, key: str, value: TaggingItem):
        self.kvstore[key] = value

    def __contains__(self, key: str):
        return key in self.kvstore

    def __iter__(self):
        return iter(self.kvstore)

    def get(self, key: str) -> TaggingItem:
        return self.kvstore[key]

    def put(self, key: str, value: TaggingItem):
        self.kvstore[key] = value

    def delete(self, key: str) -> bool:
        if key in self.kvstore:
            self.kvstore.pop(key)
            return True
        else:
            return False

    def load(self):
        try:
            with open(constants.KV_PATH, 'rb') as handle:
                saved_kvstore = pickle.load(handle)
                self.from_dict(saved_kvstore)
        except (IOError, OSError, EOFError) as e:
            self.logger.warning("Could not load local data. %s", e)

    def save(self):
        try:
            with open(constants.KV_PATH, 'wb') as handle:
                pickle.dump(self.to_dict(), handle)
        except (IOError, OSError) as e:
            self.logger.error("Could not save current session's tags to disk. %s", e)

    def to_dict(self):
        dict_ = {}
        for tag, tag_item in self.kvstore.items():
                dict_[tag] = tag_item.to_dict()
        return dict_

    def from_dict(self, dict_):
        for tag, tag_item in dict_.items():
            self.kvstore[tag] = TaggingItem.from_dict(tag_item)


class RedisKeyValueStore(BaseKeyValueStore):
    def __init__(self, ip: AnyStr, port: int):
        self.conn = redis.Redis(host=ip, port=port, db=0, charset='utf-8', decode_responses=True)

    def __getitem__(self, key: str) -> TaggingItem:
        values = self.conn.hgetall(key)
        return TaggingItem.from_dict(values)

    def __setitem__(self, key: str, value: TaggingItem):
        self.conn.hset(key, mapping=value.to_dict())

    def __contains__(self, key: str):
        return self.conn.exists(key)

    def get(self, key: str) -> TaggingItem:
        values = self.conn.hgetall(key)
        return TaggingItem.from_dict(values)

    def get_paged(self, server_id: str, count=10, cursor=0) -> Tuple[int, List]:
        return self.conn.scan(cursor=cursor, match=f"*{server_id}*", count=count)

    def put(self, key: str, value: TaggingItem):
        self.conn.hset(key, mapping=value.to_dict())

    def delete(self, key: str) -> bool:
        keys_deleted = self.conn.delete(key)
        if keys_deleted > 0:
            return True
        else:
            return False

    def save(self):
        pass
