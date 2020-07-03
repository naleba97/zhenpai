from cogs.tagging.kvstore import DictKeyValueStore
from cogs.tagging.database import TaggingDatabase, Tag


def sync_pickle_file_with_db():
    lookup = DictKeyValueStore()
    db = TaggingDatabase()
    for server_id in lookup:
        tag_names = lookup.get_tags(server_id)
        for tag_name in tag_names:
            tag_item = tag_names[tag_name]
            db.add_tag(Tag(server_id, tag_name, tag_item.url, tag_item.local_url, tag_item.creator_id))
    db.commit()


if __name__ == '__main__':
    sync_pickle_file_with_db()