from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base


class TwitcastUser(Base):
    __tablename__ = 'twitcast_users'

    twitcast_user_id = Column(Integer, primary_key=True)
    twitcast_id = Column(String, nullable=False)
    twitcast_name = Column(String, nullable=False)

    subscribers = relationship("Subscription", back_populates="twitcast_user")

    def __init__(self,
                 twitcast_user_id: int,
                 twitcast_id: str,
                 twitcast_name: str
    ):
        self.twitcast_user_id = twitcast_user_id
        self.twitcast_id = twitcast_id
        self.twitcast_name = twitcast_name
