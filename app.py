from flask import Flask, render_template, send_from_directory, redirect, session, request
from urllib.parse import quote
from video_manager import VideoManager
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications for SQLAlchemy

VIDEO_DIRECTORY = os.getenv('VIDEO_DIRECTORY')
GAMES = ["Rocket League", "Fortnite"]
video_manager = VideoManager(VIDEO_DIRECTORY, format=".mp4")

def check_session_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        game = session.get('game')
        if not game:
            return redirect('/', code=301)
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def main():
    game = session.setdefault('game', GAMES[0])
    players = video_manager.get_all_game_subdirs(game)
    player = session.setdefault('player', '')
    vid_index, vid = session.setdefault('video', video_manager.get_random_video(game=game, player=player)).values()
    video_count = video_manager.get_video_count(game, player)

    return render_template(
            'index.html', 
            game=game.upper(), 
            path_to_video=f"/video/{quote(vid['subdir'])}/{quote(vid['filename'])}", 
            player=vid['subdir'].upper(), 
            filedate=vid['filename'][-23:-4],
            vid_index=video_count - (vid_index % video_count),
            video_count=video_count,
            players = players,
            current_player = player
        )

@app.route('/video/<subdir>/<filename>')
def video(subdir, filename):
    return send_from_directory(VIDEO_DIRECTORY+subdir, filename)

@app.route('/latest-video')
@check_session_exists
def latest_video():
    session['video'] = video_manager.get_video_by_index(game=session.get('game'), player=session.get('player'), index=0)
    return redirect('/', code=301)

@app.route('/random-video')
@check_session_exists
def random_video():
    session.pop('video', None)
    return redirect('/', code=301)

@app.route('/iterate-video')
@check_session_exists
def iterate_video():
    prev_or_next = request.args.get('iterate')
    new_index = session.get('video').get('index') + (1 if prev_or_next == 'next' else - 1)
    session['video']['index'] = new_index
    session['video'] = video_manager.get_video_by_index(game=session.get('game'), player=session.get('player'), index=new_index)
    return redirect('/', code=301)

@app.route('/change-game')
@check_session_exists
def change_game():
    game_index = GAMES.index(session.get('game'))
    session['game'] = GAMES[(game_index + 1) % len(GAMES)]
    session.pop('video', None)
    session.pop('player', None)
    return redirect('/', code=301)

@app.route('/change-player')
@check_session_exists
def change_player():
    players = video_manager.get_all_game_subdirs(session.get('game'))
    player = request.args.get('player')
    session['player'] = player if player in players else ''
    session.pop('video')
    return redirect('/', code=301)
