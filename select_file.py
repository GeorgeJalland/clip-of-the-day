import os
from datetime import datetime, timedelta
from random import randrange

today = datetime.now().date()

def get_random_video(directory):
    days = 0
    eligible_vids = []
    while not eligible_vids:
        date = today - timedelta(days)
        eligible_vids = get_videos(directory, date)
        days += 1
        
    return eligible_vids[randrange(len(eligible_vids))]

def get_videos(directory, date):
        vids = os.listdir(directory)
        eligible_vids = []
        for vid_name in vids:
            filepath = os.path.join(directory, vid_name)
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid_name)

        return eligible_vids

if __name__ == "__main__":
    print(get_random_video('/Users/georg/Videos/Captures/'))