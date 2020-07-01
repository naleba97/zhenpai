from sqlalchemy import Column, Integer, String, UniqueConstraint
from .database import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)
    guild_id = Column(String, nullable=False)
    twitcast_user_id = Column(String)
    twitcast_name = Column(String)
    unique_constraint = UniqueConstraint(channel_id, twitcast_user_id)

    def __init__(self,
                 channel_id,
                 guild_id,
                 twitcast_user_id,
                 twitcast_name
    ):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.twitcast_user_id = twitcast_user_id
        self.twitcast_name = twitcast_name
