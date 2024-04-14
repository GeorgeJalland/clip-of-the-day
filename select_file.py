import os
from datetime import datetime, timedelta
from random import randrange

class VideoManager:
    def __init__(self, directory):
        self.directory = directory

    def _remove_filename_whitespace(self, files):
        for file_name in files:
            if " " in file_name:
                old_path = os.path.join(self.directory, file_name)
                new_path = os.path.join(self.directory, file_name.replace(' ', '_'))
                os.rename(old_path, new_path)
            
        return files
    
    def get_latest_video(self):
        return os.listdir(self.directory)[-1]
    
    def get_videos(self, date):
        vids = os.listdir(self.directory)
        eligible_vids = []
        for vid_name in vids:
            filepath = os.path.join(self.directory, vid_name)
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid_name)

        return eligible_vids
    
    def get_random_video(self, offset):
        today = datetime.now().date()
        days = 0
        eligible_vids = []
        while days < 30: # Only go back 30 days to avoid infinite loop
            date = today - timedelta(days)
            eligible_vids = self.get_videos(self.directory, date)
            if eligible_vids:
                if not offset:
                    eligible_vids = self._remove_filename_whitespace(self.directory, eligible_vids)
                    return eligible_vids[randrange(len(eligible_vids))]
                else:
                    offset -= 1
            days += 1
