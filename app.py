from flask import Flask, render_template, send_from_directory, redirect, session
from urllib.parse import quote
from video_manager import VideoManager

app = Flask(__name__)
app.secret_key = 'dc726efe259959c9c259996fa4ef418e'

VIDEO_DIRECTORY = '/Users/georg/OneDrive/Captures/'
GAME = "Rocket League"
video_manager = VideoManager(VIDEO_DIRECTORY, game=GAME, format=".mp4")

@app.route('/')
def main():
    vid = session.get('video', video_manager.get_nth_latest_video(0))
    return render_template('index.html', game=GAME.upper(), path_to_video=f"/video/{vid['subdir']}/{quote(vid['filename'])}", player=vid['subdir'].upper(), filedate=vid['filename'][-23:-4])

@app.route('/video/<subdir>/<filename>')
def video(subdir, filename):
    # Serve the video file using send_from_directory
    return send_from_directory(VIDEO_DIRECTORY+subdir, filename)

@app.route('/original')
def original():
    session.pop('video', None)
    session.pop('nth_latest', None)
    return redirect('/')

@app.route('/random-video')
def random_video():
    session['video'] = video_manager.get_random_video()
    session.pop('nth_latest', None)
    return redirect('/')

@app.route('/next-video')
def next_video():
    nth_latest = session.get('nth_latest', 1)
    session['video'] = video_manager.get_nth_latest_video(nth_latest)
    session['nth_latest'] = nth_latest + 1
    return redirect('/')
