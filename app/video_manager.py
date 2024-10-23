import os
from datetime import datetime
from random import randrange
from cachetools import cached, TTLCache
from typing import Dict, List

class VideoManager:
    def __init__(self, db, directory: str, format: str):
        self.db = db
        self.directory = directory
        self.format = format
    
    def get_video_by_index(self, game: str, player: str, index: int) -> Dict[int, Dict[str,str]]:
        vids = self.get_all_game_videos(game, player)
        return {'index': index, 'vid': vids[index % len(vids)]}
    
    def get_random_video(self, game: str, player: str) -> Dict[int, Dict[str,str]]:
        return self.get_video_by_index(game, player, randrange(self.get_video_count(game, player)))
    
    @cached(TTLCache(maxsize=10, ttl=600))
    def get_all_game_videos(self, game, player="") -> List[Dict[str,str]]:
        vids = []
        for root, _, files in os.walk(self.directory):
            vids += [{"subdir": os.path.basename(root), "filename":file} for file in files if game in file and self.format in file and player in os.path.basename(root)]
        return sorted(vids, key=lambda x: x['filename'], reverse=True) # return list of vids descending by date in filename

    def get_all_game_subdirs(self, game) -> List:
        return list({game_dict.get('subdir') for game_dict in self.get_all_game_videos(game)})

    def get_video_count(self, game: str, player: str) -> int:
        return len(self.get_all_game_videos(game, player))
    
    def get_videos_by_date(self, game: str, date):
        vids = self.get_all_game_videos(game)
        eligible_vids = []
        for vid in vids:
            filepath = os.path.join(self.directory, vid['subdir'], vid['filename'])
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid)

        return eligible_vids
