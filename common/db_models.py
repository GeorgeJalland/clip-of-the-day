from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    added_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
class Player(Base):
    __tablename__ = 'player'
    id = Column((Integer), primary_key=True)
    name = Column(String(50), nullable=False)
    __table_args__ = (UniqueConstraint('name', name='player_name_unique'),)

    videos = relationship("Video", back_populates="player", passive_deletes=True)

    def __repr__(self) -> str:
        return f'<Player {self.name}>'
    
class Video(Base):
    __tablename__ = 'video'
    id = Column((Integer), primary_key=True)
    player_id = Column(Integer, ForeignKey('player.id', ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    subdir_and_filename = Column(String(100), nullable=False)
    full_path = Column(String(200), nullable=False)
    thumbnail_path = Column(String(200), nullable=False)
    relative_thumbnail_path = Column(String(200), nullable=False)

    player = relationship("Player", lazy="joined")
    ratings = relationship("Rating", back_populates="video", passive_deletes=True)

    def __repr__(self) -> str:
        return f'<Video {self.name}>'

class Rating(Base):
    __tablename__ = 'rating'
    id = Column((Integer), primary_key=True)
    ip_address = Column(String(15), nullable=False)
    video_id = Column(Integer, ForeignKey('video.id', ondelete="CASCADE"), nullable=False)
    rating = Column((Integer), nullable=False)

    __table_args__ = (
        UniqueConstraint('ip_address', 'video_id', name='cant_rate_vid_twice'),
        CheckConstraint("1 <= rating <= 5"),
        Index('ix_rating_video_ip', 'video_id', 'ip_address'),
    )
    
    video = relationship("Video")
    
    def __repr__(self) -> str:
        return f'<Rating {self.id}>'
