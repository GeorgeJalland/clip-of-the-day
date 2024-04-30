from flask import Flask, render_template, send_from_directory, redirect, session, request
from urllib.parse import quote
from app.video_manager import VideoManager
from app.db_models import db, submit_rating, get_ratings_by_player
from config import Config

video_manager = VideoManager(Config.VIDEO_DIRECTORY, format=".mp4")

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    GAMES = app.config.get('GAMES')

    @app.route('/', methods=['GET', 'POST'])
    def main():
        player = session.setdefault('player', '')
        game = session.setdefault('game', GAMES[0])
        vid_index, vid = session.setdefault('video', video_manager.get_random_video(game=game, player=player)).values()
        video_count = video_manager.get_video_count(game, player)
        players = video_manager.get_all_game_subdirs(game)

        if request.method == 'POST':
            rating_ = request.form.get('rating')
            player_ = request.form.get('player')
            video_ = request.form.get('video')
            ip_address = request.remote_addr
            # add rating to database
            submit_rating(ip_address=ip_address, video=video_, player=player_, rating=rating_)


        return render_template(
                'index.html', 
                game=game.upper(), 
                path_to_video=f"/video/{quote(vid['subdir'])}/{quote(vid['filename'])}", 
                player=vid['subdir'].upper(), 
                video_name=vid['filename'],
                vid_index=video_count - (vid_index % video_count),
                video_count=video_count,
                players = players,
                selected_player = player,
            )

    @app.route('/video/<subdir>/<filename>')
    def video(subdir, filename):
        return send_from_directory(Config.VIDEO_DIRECTORY+subdir, filename)

    @app.route('/latest-video')
    def latest_video():
        session['video'] = video_manager.get_video_by_index(game=session.get('game'), player=session.get('player'), index=0)
        return redirect('/')

    @app.route('/random-video')
    def random_video():
        session.pop('video', None)
        return redirect('/')

    @app.route('/iterate-video')
    def iterate_video():
        prev_or_next = request.args.get('iterate')
        new_index = session.get('video').get('index') + (1 if prev_or_next == 'next' else - 1)
        session['video']['index'] = new_index
        session['video'] = video_manager.get_video_by_index(game=session.get('game'), player=session.get('player'), index=new_index)
        return redirect('/')

    @app.route('/change-game')
    def change_game():
        game_index = GAMES.index(session.get('game'))
        session['game'] = GAMES[(game_index + 1) % len(GAMES)]
        session.pop('video', None)
        session.pop('player', None)
        return redirect('/')

    @app.route('/change-player')
    def change_player():
        player = request.args.get('player')
        session['player'] = player
        session.pop('video')
        return redirect('/')
    
    return app
