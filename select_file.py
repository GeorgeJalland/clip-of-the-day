import os
from datetime import datetime, timedelta
from random import randrange
import shutil

def copy_file(source_path, destination_path):
    shutil.copy(source_path, destination_path)


original_name = "Rocket League (64-bit, DX11, Cooked) 2024-04-12 17-32-37.mp4"

today = datetime.now().date() - timedelta(3)

directory = '/Users/georg/Videos/Captures'
files = os.listdir(directory)
files_created_today = []

for filename in files:
    filepath = os.path.join(directory, filename)
    created_time = datetime.fromtimestamp(os.path.getctime(filepath))
    if created_time.date() == today:
        files_created_today.append(filename)
