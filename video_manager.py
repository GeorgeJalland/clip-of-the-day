import os
from datetime import datetime
from random import randrange
from cachetools import cached, TTLCache

class VideoManager:
    def __init__(self, directory, format):
        self.directory = directory
        self.format = format

    def return_dict(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return {'index': result[0], 'vid': result[1]}
        return wrapper
    
    @return_dict
    def get_nth_latest_video(self, game, n):
        vids = self.get_all_game_videos(game)
        index = len(vids) - (n % len(vids)) - 1 # loop back to latest video if end of list reached
        return index, sorted(vids, key=lambda x: x['filename'])[index]
    
    @cached(TTLCache(maxsize=10, ttl=600))
    def get_all_game_videos(self, game):
        vids = []
        for root, _, files in os.walk(self.directory):
            vids += [{"subdir": os.path.basename(root), "filename":file} for file in files if game in file and self.format in file]
        return vids
    
    def get_video_count(self, game):
        return len(self.get_all_game_videos(game))
    
    def get_videos_by_date(self, game, date):
        vids = self.get_all_game_videos(game)
        eligible_vids = []
        for vid in vids:
            filepath = os.path.join(self.directory, vid['subdir'], vid['filename'])
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid)

        return eligible_vids

    @return_dict
    def get_random_video(self, game):
        vids = self.get_all_game_videos(game)
        index = randrange(len(vids))
        return index, vids[index]
