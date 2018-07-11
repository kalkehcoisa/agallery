from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    event,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table
)
from sqlalchemy.orm import relationship

from agallery.models.meta import Base
from agallery.models import types


class Likes(Base):
    __tablename__ = 'likes'

    photo_id = Column(String, ForeignKey('photo.uid'), primary_key=True)
    user_id = Column(String, ForeignKey('user.login'), primary_key=True)


class Photo(Base):
    __tablename__ = 'photo'

    uid = Column(types.UUIDType, primary_key=True, default=uuid.uuid4)
    url = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey('user.login'))
    user = relationship("auth.User")

    sent_date = Column(DateTime, nullable=False, default=datetime.now)
    likes_count = Column(Integer, nullable=False, default=0)
    approved = Column(Boolean(name='bool'), default=False, nullable=False)

    likes = relationship(
        "auth.User",
        secondary=Likes.__table__,
        back_populates="likes",
        collection_class=set
    )

    @property
    def likes_ids(self):
        # raise Exception(self.likes)
        if self.likes is None:
            return set()
        return set(u.login for u in self.likes)

    def __str__(self):
        return self.title
