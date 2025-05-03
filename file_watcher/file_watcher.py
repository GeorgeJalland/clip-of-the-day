import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler
import os

from common.config import Config
from common.logger import get_logger
from file_watcher.db import add_new_player_record, add_new_video_record, delete_player_record, delete_video_record, get_db, create_schema
from file_watcher.thumbnail import ThumbnailGenerator, get_thumbnail_path
from file_watcher.migrations import migrate_video_data, generate_missing_thumbnails

logger = get_logger("file_watcher")

db = get_db()

create_schema(db)

class Watcher:

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        logger.info(f"Watcher Running in {format(self.directory)}.")
        logger.info(f"Watcher connected to db: {Config.SQLALCHEMY_DATABASE_URI}")
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        logger.info("Watcher Terminated\n")


class VideoFileHandler(FileSystemEventHandler):

    def __init__(self, thumbail_generator: ThumbnailGenerator):
        super().__init__()
        self.thumbnail_generator = thumbail_generator

    def on_created(self, event):
        if event.is_directory:
            if event.src_path == "thumbnails":
                return
            logger.info(f"new directory detected: {event}")
            player_name = os.path.basename(event.src_path)
            add_new_player_record(db, player_name)
        else:
            logger.info(f"new file detected: {event}")
            if not event.src_path.endswith(".mp4"):
                logger.info("file not video format")
                return
            self.create_thumbail_and_video_record(event.src_path)

    def on_moved(self, event):
        logger.info(f"file moved: {event}")
        if event.is_directory:
            logger.info(f"directory moved {event}")
            # do something?
        else:
            if event.src_path.endswith(".mp4.tmp") and event.dest_path.endswith(".mp4"):
                logger.info(f"New syncthing video detected: {event.dest_path}")
                self.create_thumbail_and_video_record(event.dest_path)

    def create_thumbail_and_video_record(self, event_path):
        video_name = os.path.basename(event_path)
        player_name = os.path.basename(os.path.dirname(event_path))
        subdir_and_filename = player_name+'/'+video_name
        full_path = event_path
        thumbnail_output_path = get_thumbnail_path(event_path)
        thumbnail_path = self.thumbnail_generator.delayed_generate(event_path, output_path=thumbnail_output_path)
        add_new_video_record(db, player_name, video_name, subdir_and_filename, full_path, thumbnail_path)

    def on_deleted(self, event):
        if event.is_directory:
            if event.src_path == "thumbnails":
                return
            # since on delete cascade this will drop all videos for given player too
            logger.info(f"directory deleted: {event}")
            player_name = os.path.basename(event.src_path)
            delete_player_record(db, player_name)
        else:
            logger.info(f"file deleted: {event}")
            if event.src_path.endswith(".mp4"):
                video_name = os.path.basename(event.src_path)
                player_name = os.path.basename(os.path.dirname(event.src_path))
                delete_video_record(db, player_name, video_name)
                return
            if event.src_path.endswith(".jpg"):
                logger.info(f"thumbnail deleted: {event}")
                return
                 
if __name__=="__main__":
    migrate_video_data(db, Config.VIDEO_DIRECTORY)
    generate_missing_thumbnails(db)
    thumbnail_generator = ThumbnailGenerator()
    w = Watcher(directory=Config.VIDEO_DIRECTORY, handler=VideoFileHandler(thumbnail_generator))
    w.run()
