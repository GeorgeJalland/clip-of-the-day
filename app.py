from flask import Flask, render_template, send_from_directory, redirect, session, request
from urllib.parse import quote
from video_manager import VideoManager
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

VIDEO_DIRECTORY = os.getenv('VIDEO_DIRECTORY')
GAME = "Rocket League"
video_manager = VideoManager(VIDEO_DIRECTORY, format=".mp4")

@app.route('/')
def main():
    game = session.get('game', GAME)
    vid = session.get('video', video_manager.get_nth_latest_video(game=game, n=0))
    return render_template('index.html', game=game.upper(), path_to_video=f"/video/{vid['subdir']}/{quote(vid['filename'])}", player=vid['subdir'].upper(), filedate=vid['filename'][-23:-4])

@app.route('/video/<subdir>/<filename>')
def video(subdir, filename):
    # Serve the video file using send_from_directory
    return send_from_directory(VIDEO_DIRECTORY+subdir, filename)

@app.route('/latest-video')
def latest_video():
    session.pop('video', None)
    session.pop('nth_latest', None)
    return redirect('/')

@app.route('/random-video')
def random_video():
    session['video'] = video_manager.get_random_video(game=session.get('game', GAME))
    session.pop('nth_latest', None)
    return redirect('/')

@app.route('/iterate-video')
def iterate_video():
    prev_or_next = request.args.get('iterate')
    session['nth_latest'] = session.get('nth_latest', 0) + (1 if prev_or_next == 'next' else - 1)
    session['video'] = video_manager.get_nth_latest_video(game=session.get('game', GAME), n=session['nth_latest'])
    return redirect('/')

@app.route('/change-game')
def change_game():
    session['game'] = "Fortnite" if session.get('game') == GAME else GAME
    return redirect('/')
