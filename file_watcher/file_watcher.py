import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler
import os
import logging

from common.config import Config
from file_watcher.db import add_new_player_record, add_new_video_record, delete_player_record, delete_video_record, migrate_video_data, get_db, create_schema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("file_watcher")

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

    def on_created(self, event):
        if event.is_directory:
            logger.info(f"new directory detected: {event}")
            player_name = os.path.basename(event.src_path)
            add_new_player_record(db, player_name)
        else:        
            logger.info(f"new file detected: {event}")
            video_name = os.path.basename(event.src_path)
            if video_name[-4:] != ".mp4":
                logger.info("file not video format")
                return
            player_name = os.path.basename(os.path.dirname(event.src_path))
            subdir_and_filename = player_name+'/'+video_name
            full_path = event.src_path
            add_new_video_record(db, player_name, video_name, subdir_and_filename, full_path)

    def on_moved(self, event):
        logger.info(f"file moved: {event}")
        if event.is_directory:
            logger.info(f"directory moved {event}")
            # do something?
        else:
            if event.src_path.endswith(".mp4.tmp") and event.dest_path.endswith(".mp4"):
                logger.info(f"New syncthing video detected: {event.dest_path}")
                video_name = os.path.basename(event.dest_path)
                player_name = os.path.basename(os.path.dirname(event.dest_path))
                subdir_and_filename = player_name+'/'+video_name
                full_path = event.dest_path
                add_new_video_record(db, player_name, video_name, subdir_and_filename, full_path)

    def on_deleted(self, event):
        if event.is_directory:
            # since on delete cascade this will drop all videos for given player too
            logger.info(f"directory deleted: {event}")
            player_name = os.path.basename(event.src_path)
            delete_player_record(db, player_name)
        else:
            logger.info(f"file deleted: {event}")
            video_name = os.path.basename(event.src_path)
            player_name = os.path.basename(os.path.dirname(event.src_path))
            delete_video_record(db, player_name, video_name)

if __name__=="__main__":
    migrate_video_data(db, Config.VIDEO_DIRECTORY)
    w = Watcher(directory=Config.VIDEO_DIRECTORY, handler=VideoFileHandler())
    w.run()
