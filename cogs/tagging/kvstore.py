import typing

class TaggingItem(object):
    """
    Thing to be retrieved, can be an image file, a gif, a soundbite, 
    a url with an embed preview, a youtube link, a text document, etc.
    """
    pass

class BaseKeyValueStore(object):
    def get(self, key: str) -> TaggingItem:
        raise NotImplementedError

    def get_all(self) -> Generator[TaggingItem, None, None]: # I'm pretty sure this is just __iter__()
        raise NotImplementedError

    def __contains__(self, key: str):
        raise NotImplementedError

class DictKeyValueStore(BaseKeyValueStore):
    def __init__(self):
        self.kvstore = {} # TODO: load from a pickle file, not sure when we save though

    def get(self, key: str) -> TaggingItem:
        return self.kvstore.get(key)

    def __contains__(self, key: str):
        return key in self.kvstore
