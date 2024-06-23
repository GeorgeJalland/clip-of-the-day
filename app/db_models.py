from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from sqlalchemy.orm import Session
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

    player = relationship("Player", lazy="joined")
    ratings = relationship("Rating", back_populates="video", passive_deletes=True)

    def __repr__(self) -> str:
        return f'<Video {self.name}>'

class Rating(Base):
    __tablename__ = 'rating'
    id = Column((Integer), primary_key=True)
    ip_address = Column(String(15), nullable=False)
    video_id = Column(Integer, ForeignKey('video.id'), nullable=False)
    rating = Column((Integer), nullable=False)
    __table_args__ = (UniqueConstraint('ip_address', 'video_id', name='cant_rate_vid_twice'),
                      CheckConstraint("1 <=  rating <= 5"),)
    
    video = relationship("Video")
    
    def __repr__(self) -> str:
        return f'<Rating {self.id}>'
    
def migrate_video_data(db, video_directory, file_format=".mp4"):
    def get_videos_in_filesystem():
        videos = set()
        for root, _, files in os.walk(video_directory):
            player = os.path.basename(root)
            if not player or player[0:1] == ".":
                continue
            for file in files:
                if file[-4:] == file_format:
                    videos.add((player, file, video_directory+'/'+player+'/'+file))
        return videos

    def get_videos_in_database():
        return {(video.player.name, video.name, video.full_path) for video in get_all_videos(db)}
    
    logger.info("migrating video data")

    videos_in_filesystem = get_videos_in_filesystem()
    videos_in_database = get_videos_in_database()

    # if video in filesystem and not db; add record
    vids_not_in_database = videos_in_filesystem - videos_in_database
    for video in vids_not_in_database:
        add_new_video_record(db=db, player_name=video[0], video_name=video[1], subdir_and_filename=video[0]+'/'+video[1], full_video_path=video[2])
        
    # if video in db but not file system; delete record
    vids_not_in_filesystem = videos_in_database - videos_in_filesystem
    for video in vids_not_in_filesystem:
        delete_video_record(db=db, player_name=video[0], video_name=video[1])

    logger.info("migration complete")


def submit_rating(db, ip_address, video, player, rating):
    with Session(db) as session:
        existing_rating = session.query(Rating).filter_by(ip_address=ip_address, video=video, player=player).one_or_none()
        if existing_rating:
            existing_rating.rating = rating
        else:
            new_rating = Rating(ip_address=ip_address, video=video, player=player, rating=rating)
            session.add(new_rating)
        session.commit()

def get_ratings_for_video(db, video):
    # return dictionary of sum ratings, ratings count, avg rating
    pass

def get_ratings_by_player(db, game):
    # needs reworking
    with Session(db) as session:
        # cache for 1 minute?
        result = session.query(
            Rating.player,
            func.sum(Rating.rating),
            func.avg(Rating.rating)
        ).filter(Rating.video.contains(game)).group_by(Rating.player).all()
        return [{'player': row[0], 'sum_ratings': row[1], 'avg_rating': row[2]} for row in result]

def get_user_video_rating(db, video, ip_address) -> int:
    # return the rating of a given video for given ip_address
    pass

def get_all_videos(db):
    with Session(db) as session:
        vids = session.query(Video).all()
    return vids

def add_new_video_record(db, player_name, video_name, subdir_and_filename, full_video_path):
    logger.info(f"creating new video record for {video_name}")
    with Session(db) as session:
        player = session.query(Player).filter_by(name=player_name).first()
        player_id = player.id if player else add_new_player_record(db, player_name)
        new_video = Video(player_id=player_id, name=video_name, subdir_and_filename=subdir_and_filename, full_path=full_video_path)
        session.add(new_video)
        session.commit()
        new_video_id = new_video.id
        logger.info(f"new video record added: {new_video}")
    return new_video_id

def add_new_player_record(db, player_name):
    # catch not unique exception?
    logger.info(f"creating new player record for {player_name}")
    with Session(db) as session:
        new_player = Player(name=player_name)
        session.add(new_player)
        session.commit()
        new_player_id = new_player.id
        logger.info(f"new player record created: {new_player}")
    return new_player_id

def delete_player_record(db, player_name):
    logger.info(f"deleting player {player_name} and all associated videos")
    with Session(db) as session:
        session.query(Player).filter_by(name=player_name).delete()
        session.commit()
        logger.info(f"deleted player {player_name} and all associated videos")

def delete_video_record(db, player_name, video_name):
    logger.info(f"deleting video {video_name} by player {player_name}")
    with Session(db) as session:
        player = session.query(Player).filter_by(name=player_name).first()
        session.query(Video).filter_by(player_id=player.id, name=video_name).delete()
        session.commit()
        logger.info("video deleted")    
