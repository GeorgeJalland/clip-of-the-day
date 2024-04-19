import os
from datetime import datetime
from random import randrange
from cachetools import cached, TTLCache

class VideoManager:
    def __init__(self, directory, game, format):
        self.directory = directory
        self.game = game
        self.format = format
    
    def get_nth_latest_video(self, n):
        vids = self.get_all_game_videos()
        index = -(n % len(vids)) - 1 # loop back to latest video if end of list reached
        return sorted(vids, key=lambda x: x['filename'])[index]
    
    @cached(TTLCache(maxsize=1, ttl=600))
    def get_all_game_videos(self):
        vids = []
        for root, _, files in os.walk(self.directory):
            vids += [{"subdir": os.path.basename(root), "filename":file} for file in files if self.game in file and self.format in file]
        return vids
    
    def get_videos_by_date(self, date):
        vids = self.get_all_game_videos()
        eligible_vids = []
        for vid in vids:
            filepath = os.path.join(self.directory, vid['subdir'], vid['filename'])
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid)

        return eligible_vids

    def get_random_video(self):
        vids = self.get_all_game_videos()
        return vids[randrange(len(vids))]
