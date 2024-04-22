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

def get_all_videos(db):
    with Session(db) as session:
        vids = session.query(Video).all()
    return vids

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
    
    logger.info("--------------------------- migrating video data ---------------------------")

    videos_in_filesystem = get_videos_in_filesystem()
    videos_in_database = get_videos_in_database()

    # if video in filesystem and not db; add record
    vids_not_in_database = videos_in_filesystem - videos_in_database
    # sort videos by video name so added in correct order
    for video in sorted(list(vids_not_in_database), key=lambda item: item[1]):
        add_new_video_record(db=db, player_name=video[0], video_name=video[1], subdir_and_filename=video[0]+'/'+video[1], full_video_path=video[2])
        
    # if video in db but not file system; delete record
    vids_not_in_filesystem = videos_in_database - videos_in_filesystem
    for video in vids_not_in_filesystem:
        delete_video_record(db=db, player_name=video[0], video_name=video[1])

    logger.info("--------------------------- migration complete ---------------------------")