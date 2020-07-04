from sqlalchemy import Column, Integer, String, UniqueConstraint
from .database import Base


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    guild_id = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    cdn_url = Column(String, nullable=False)
    local_url = Column(String, nullable=False)
    creator_id = Column(String, nullable=False)
    unique_constraint = UniqueConstraint(guild_id, tag)

    def __init__(self,
                 guild_id: str,
                 tag: str,
                 cdn_url: str,
                 local_url: str,
                 creator_id: str
    ):
        self.guild_id = guild_id
        self.tag = tag
        self.cdn_url = cdn_url
        self.local_url = local_url
        self.creator_id = creator_id
