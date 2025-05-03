from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
import logging
import os
from sqlalchemy.orm import Session

from common.config import Config
from common.db_models import Video, Player, Base

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_db():
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)

def create_schema(engine):
    Base.metadata.create_all(engine)

def add_new_video_record(db, player_name, video_name, subdir_and_filename, full_video_path, thumbnail_path, relative_thumbnail_path):
    logger.info(f"creating new video record for {video_name}")
    with Session(db) as session:
        player = session.query(Player).filter_by(name=player_name).first()
        player_id = player.id if player else add_new_player_record(db, player_name)
        new_video = Video(player_id=player_id, name=video_name, subdir_and_filename=subdir_and_filename, full_path=full_video_path, thumbnail_path=thumbnail_path, relative_thumbnail_path=relative_thumbnail_path)
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
        query = session.query(Video).filter_by(player_id=player.id, name=video_name)
        video = query.scalar()
        query.delete()
        session.commit()
        if video.thumbnail_path:
            os.remove(video.thumbnail_path)
        logger.info("video and thumbnail deleted")

def get_all_videos(db):
    with Session(db) as session:
        vids = session.query(Video).all()
    return vids
