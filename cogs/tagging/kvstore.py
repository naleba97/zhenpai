import abc
import pickle
import redis
from os import path
from typing import Dict
from typing import AnyStr
from typing import List
from typing import Tuple

from .constants import *
from .taggingutils import *

class TaggingItem(object):
    """
    Thing to be retrieved, can be an image file, a gif, a soundbite, 
    a url with an embed preview, a youtube link, a text document, etc.
    """

    def __init__(self, name: str = None, url: str = None, local_url: str = None, creator_id: int = None):
        self._name = name
        self._url = url
        self._local_url = local_url
        self._creator_id = creator_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

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

    @property
    def creator_id(self):
        return self._creator_id

    @creator_id.setter
    def creator_id(self, value):
        self._creator_id = value

    def to_dict(self):
        result = {
            key[1:]: getattr(self, key)
            for key in self.__dict__
            if key[0] == '_' and hasattr(self, key)
        }
        return result

    def from_dict(self, data):
        for attr in ('name', 'url', 'local_url', 'creator_id'):
            try:
                value = data[attr]
            except KeyError:
                continue
            else:
                setattr(self, '_' + attr, value)
        return self


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
        self.kvstore: Dict[str, TaggingItem] = {}  # TODO: load from a pickle file, not sure when we save though

    def __getitem__(self, key: str) -> TaggingItem:
        return self.kvstore.get(key)

    def __setitem__(self, key: str, value: TaggingItem):
        self.kvstore[key] = value

    def __contains__(self, key: str):
        return key in self.kvstore

    def __iter__(self):
        return iter(self.kvstore.items())

    def get(self, key: str) -> TaggingItem:
        return self.kvstore.get(key)

    def put(self, key: str, value: TaggingItem):
        self.kvstore[key] = value
        return self

    def load(self, file):
        try:
            with open(file, 'rb') as handle:
                saved_kvstore = pickle.load(handle)
                self.from_dict(saved_kvstore)
        except (IOError, OSError, EOFError) as e:
            print("Warn: could not load tags from disk")
        return self

    def save(self, file):
        try:
            with open(file, 'wb') as handle:
                pickle.dump(self.to_dict(), handle)
        except (IOError, OSError) as e:
            print("Fatal: could not save tags")

    def to_dict(self):
        dict_ = {}
        for k, v in self:
            dict_[k] = v.to_dict()
        return dict_

    def from_dict(self, dict_):
        for k, v in dict_.items():
            self.kvstore[k] = TaggingItem().from_dict(v)


class RedisKeyValueStore(BaseKeyValueStore):
    def __init__(self, ip: AnyStr, port: int):
        self.conn = redis.Redis(host=ip, port=port, db=0, charset='utf-8', decode_responses=True)

    def __getitem__(self, key: str) -> TaggingItem:
        values = self.conn.hgetall(key)
        return TaggingItem().from_dict(values)

    def __setitem__(self, key: str, value: TaggingItem):
        self.conn.hset(key, mapping=value.to_dict())

    def __contains__(self, key: str):
        return self.conn.exists(key)

    def get(self, key: str) -> TaggingItem:
        values = self.conn.hgetall(key)
        return TaggingItem().from_dict(values)

    def get_paged(self, server_id: str, count=10, cursor=0) -> Tuple[int, List]:
        return self.conn.scan(cursor=cursor, match="*{0}*".format(server_id), count=count)

    def put(self, key: str, value: TaggingItem):
        self.conn.hset(key, mapping=value.to_dict())

    def save(self):
        pass
