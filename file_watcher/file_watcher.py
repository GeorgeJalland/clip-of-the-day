import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from config import Config
from app.db_models import new_video_record
from sqlalchemy import create_engine
import logging#

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("file_watcher")

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
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        logger.info("Watcher Terminated\n")


class VideoFileHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        if event.event_type == "created":
            logger.info(f"new file detected: {event}")
            player = os.path.basename(os.path.dirname(event.src_path))
            video_name = os.path.dirname(event.src_path)
            subdir_and_filename = player+'/'+video_name
            full_path = event.src_path
            new_video_record(db, player, video_name, subdir_and_filename, full_path)


if __name__=="__main__":
    w = Watcher(directory=Config.VIDEO_DIRECTORY, handler=VideoFileHandler())
    w.run()
