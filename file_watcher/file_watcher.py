import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler
import os
from config import Config
from db_models import new_video_record, new_player_record, delete_player_record
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("file_watcher")

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

db = create_engine(Config.SQLALCHEMY_DATABASE_URI)

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
            new_player_record(db, player_name)
        else:        
            logger.info(f"new file detected: {event}")
            video_name = os.path.basename(event.src_path)
            if video_name[-4:] != ".mp4":
                logger.info("file not video format")
                return
            player_name = os.path.basename(os.path.dirname(event.src_path))
            subdir_and_filename = player_name+'/'+video_name
            full_path = event.src_path
            new_video_record(db, player_name, video_name, subdir_and_filename, full_path)

    def on_moved(self, event):
        if event.is_directory:
            logger.info(f"directory moved {event}")
            # take destination path and update player name
            # update video name method?

    def on_deleted(self, event):
        if event.is_directory:
            # since on delete cascade this will drop all videos for given player too
            logger.info(f"directory deleted: {event}")
            player_name = os.path.basename(event.src_path)
            delete_player_record(db, player_name)

    def on_any_event(self, event: FileSystemEvent) -> None:
        # remove once finished
        logger.info(event)

if __name__=="__main__":
    # apply migration arg, pass via env var in docker compose up
    # migrate database with changes, scan all dirs and add records
    w = Watcher(directory=Config.VIDEO_DIRECTORY, handler=VideoFileHandler())
    w.run()
