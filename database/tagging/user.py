from sqlalchemy import Column, Integer, String, UniqueConstraint
from database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    counter = Column(Integer, nullable=False)
    unique_constraint = UniqueConstraint(user_id, tag)

    def __init__(self,
                 user_id: str,
                 tag: str,
                 counter: int
    ):
        self.user_id = user_id
        self.tag = tag
        self.counter = counter
