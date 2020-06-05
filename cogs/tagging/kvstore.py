import abc
import pickle
from os import path
from typing import Dict


class TaggingItem(object):
    """
    Thing to be retrieved, can be an image file, a gif, a soundbite, 
    a url with an embed preview, a youtube link, a text document, etc.
    """

    def __init__(self, url: str = None, local_url: str = None, creator_id: int = None):
        self._url = url
        self._local_url = local_url
        self._creator_id = creator_id
        self._counter = 0

    @property
    def url(self):
        return self._url

    @property
    def local_url(self):
        return self._local_url

    @property
    def creator_id(self):
        return self._creator_id

    @property
    def counter(self):
        return self._counter

    @counter.setter
    def counter(self, value: int):
        self._counter = value

    @local_url.setter
    def local_url(self, value):
        self._local_url = value

    @url.setter
    def url(self, value):
        self._url = value

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
        for attr in ('url', 'local_url', 'creator_id', 'counter'):
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
