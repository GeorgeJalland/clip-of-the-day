import os
from datetime import datetime
from random import randrange
from cachetools import cached, TTLCache
from typing import Dict, List
from sqlalchemy.orm import Session

from app import db

class VideoManager:
    def __init__(self, directory: str, format: str):
        self.directory = directory
        self.format = format
    
    def get_video_by_index(self, session: Session, index: int) -> Dict[int, Dict[str,str]]:
        normalised_index = index % db.get_video_count(session)
        vid_and_ratings = db.get_video_and_ratings(session, normalised_index)
        print(vid_and_ratings)
        return {'index': vid_and_ratings[0], 'name_and_subdir': vid_and_ratings[1], "player": vid_and_ratings[2]}
    
    def get_random_video(self, session: Session, game: str, player: str) -> Dict[int, Dict[str,str]]:
        return self.get_video_by_index(session, randrange(db.get_video_count(session)))
    
    @cached(TTLCache(maxsize=10, ttl=600))
    def get_all_game_videos(self, game, player="") -> List[Dict[str,str]]:
        vids = []
        for root, _, files in os.walk(self.directory):
            vids += [{"subdir": os.path.basename(root), "filename":file} for file in files if game in file and self.format in file and player in os.path.basename(root)]
        return sorted(vids, key=lambda x: x['filename'], reverse=True) # return list of vids descending by date in filename

    def get_all_game_subdirs(self, game) -> List:
        return list({game_dict.get('subdir') for game_dict in self.get_all_game_videos(game)})

    def get_video_count(self, session: Session, game: str = None, player: str = None) -> int:
        return db.get_video_count(session)
    
    def get_videos_by_date(self, game: str, date):
        vids = self.get_all_game_videos(game)
        eligible_vids = []
        for vid in vids:
            filepath = os.path.join(self.directory, vid['subdir'], vid['filename'])
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid)

        return eligible_vids
