import os
from datetime import datetime
from random import randrange
from cachetools import cached, TTLCache
from typing import Dict

class VideoManager:
    def __init__(self, directory: str, format: str):
        self.directory = directory
        self.format = format
    
    def get_video_by_index(self, game: str, index: int) -> Dict[int, Dict[str,str]]:
        vids = self.get_all_game_videos(game)
        return {'index': index, 'vid': vids[index % len(vids)]}
    
    def get_random_video(self, game: str) -> Dict[int, Dict[str,str]]:
        return self.get_video_by_index(game, randrange(self.get_video_count(game)))
    
    @cached(TTLCache(maxsize=10, ttl=600))
    def get_all_game_videos(self, game) -> Dict[str,str]:
        vids = []
        for root, _, files in os.walk(self.directory):
            vids += [{"subdir": os.path.basename(root), "filename":file} for file in files if game in file and self.format in file]
        return sorted(vids, key=lambda x: x['filename'], reverse=True) # return list of vids descending by date in filename
    
    def get_video_count(self, game: str) -> int:
        return len(self.get_all_game_videos(game))
    
    def get_videos_by_date(self, game: str, date):
        vids = self.get_all_game_videos(game)
        eligible_vids = []
        for vid in vids:
            filepath = os.path.join(self.directory, vid['subdir'], vid['filename'])
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid)

        return eligible_vids
