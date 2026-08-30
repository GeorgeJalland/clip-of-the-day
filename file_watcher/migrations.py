import os

from file_watcher.thumbnail import get_thumbnail_path, ThumbnailGenerator
from common.logger import get_logger
from common.config import Config
from file_watcher.db import get_all_videos, add_new_video_record, delete_video_record

logger = get_logger(__name__)

# TODO: path joins shoudl be os.path.join instead of string concatenation
# TODO: path generation should be in one place, not spread across multiple files

def migrate_video_data(db, video_directory, file_format=".mp4"):
    
    logger.info("--------------------------- migrating video data ---------------------------")

    videos_in_filesystem = get_videos_in_filesystem(video_directory, file_format)
    videos_in_database = get_videos_in_database(db)

    # if video in filesystem and not db; add record
    vids_not_in_database = videos_in_filesystem - videos_in_database
    # sort videos by video name so added in correct order
    thumbnail_generator = ThumbnailGenerator()
    for video in sorted(list(vids_not_in_database), key=lambda item: item[1]):
        player_name = video[0]
        video_name = video[1]
        video_path = os.path.join(video_directory, video[0], video[1])
        thumbnail_path = get_thumbnail_path(video_path)
        relative_thumbnail_path = os.path.join(player_name, Config.THUMBNAIL_DIRECTORY_NAME, os.path.basename(thumbnail_path))
        if not os.path.exists(thumbnail_path):
            thumbnail_generator.generate(video_path, thumbnail_path)
        add_new_video_record(db=db, player_name=player_name, video_name=video_name, subdir_and_filename=os.path.join(player_name, video[1]), full_video_path=video_path, thumbnail_path=thumbnail_path, relative_thumbnail_path=relative_thumbnail_path)

    # if video in db but not file system; delete record
    vids_not_in_filesystem = videos_in_database - videos_in_filesystem
    for video in vids_not_in_filesystem:
        delete_video_record(db=db, player_name=video[0], video_name=video[1])

    logger.info("--------------------------- migration complete ---------------------------")

def get_videos_in_filesystem(video_directory, file_format=".mp4") -> set:
    videos = set()
    for root, _, files in os.walk(video_directory):
        player = os.path.basename(root)
        if not player or player[0:1] == ".":
            continue
        for file in files:
            if file[-4:] == file_format:
                videos.add((player, file))
    return videos

def get_videos_in_database(db) -> set:
    return {(video.player.name, video.name) for video in get_all_videos(db)}

def generate_missing_thumbnails(db):
    logger.info("--------------------------- generating missing thumbnails ---------------------------")
    videos = get_all_videos(db)
    thumbnail_generator = ThumbnailGenerator()
    for video in videos:
        if video.thumbnail_path is None or not os.path.exists(video.thumbnail_path):
            thumbnail_generator.generate(video.full_path, video.thumbnail_path)
    logger.info("--------------------------- thumbnail generation complete ---------------------------")