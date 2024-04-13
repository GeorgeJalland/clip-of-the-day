import os
from datetime import datetime, timedelta
from random import randrange

today = datetime.now().date()

def get_random_video(directory, offset = 0):
    offset = offset
    days = 0
    eligible_vids = []
    while days < 30: # Only go back 30 days to avoid infinite loop
        date = today - timedelta(days)
        eligible_vids = get_videos(directory, date)
        if eligible_vids:
            if not offset:
                eligible_vids = remove_filename_whitespace(directory, eligible_vids)
                return eligible_vids[randrange(len(eligible_vids))]
            else:
                 offset -= 1
        days += 1


def get_videos(directory, date):
        vids = os.listdir(directory)
        eligible_vids = []
        for vid_name in vids:
            filepath = os.path.join(directory, vid_name)
            created_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if created_time.date() == date:
                eligible_vids.append(vid_name)

        return eligible_vids

def remove_filename_whitespace(directory, files):
    for file_name in files:
         if " " in file_name:
            old_path = os.path.join(directory, file_name)
            new_path = os.path.join(directory, file_name.replace(' ', '_'))
            os.rename(old_path, new_path)
        
    return files
     

if __name__ == "__main__":
    print(get_random_video('/Users/georg/Videos/Captures/', offset=1))