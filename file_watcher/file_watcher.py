import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from config import Config

class Watcher:

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        print("\nWatcher Terminated\n")


class VideoFileHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        if event.event_type == "created":
            print(f"Hello George, new file created: {event.src_path}")
            print(f"Hello George, in directory: {os.path.basename(os.path.dirname(event.src_path))}")

if __name__=="__main__":
    w = Watcher(directory=Config.VIDEO_DIRECTORY, handler=VideoFileHandler())
    w.run()
