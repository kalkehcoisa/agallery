from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table
)
from sqlalchemy.orm import relationship

from agallery.models.meta import Base


likes_table = Table(
    'likes',
    Base.metadata,
    Column('photo_id', String, ForeignKey('photo.url')),
    Column('user_id', String, ForeignKey('user.login'))
)


class Photo(Base):
    __tablename__ = 'photo'

    url = Column(String, primary_key=True)

    user_id = Column(String, ForeignKey('user.login'))
    user = relationship("auth.User")

    sent_date = Column(DateTime, nullable=False, default=datetime.now)
    likes_count = Column(Integer, nullable=False, default=0)
    approved = Column(Boolean(name='bool'), default=False, nullable=False)

    likes = relationship(
        "auth.User",
        secondary=likes_table,
        back_populates="likes")

    def __str__(self):
        return self.title
