from flask import Flask, session, request, g, jsonify
from urllib.parse import quote

from app.db import SessionLocal, create_schema, submit_rating, get_players_with_ratings, get_video_and_ratings, get_vid_count
from common.config import Config

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        create_schema()

    GAMES = app.config.get('GAMES')

    @app.before_request
    def create_session():
        # Create a new session for each request
        g.db = SessionLocal()

    @app.teardown_request
    def remove_session(error=None):
        # Ensure the session is properly closed after each request
        SessionLocal.remove()

    @app.get('/players')
    def get_players():
        # need to remove concept of game, make it rocket league only?
        game = request.args.get('game', GAMES[0])
        return jsonify(get_players_with_ratings(g.db, game))

    @app.get('/video/<int:video_id>')
    def get_video(video_id: int):
        # add default value for video_id which is random ?
        ip_addr = request.remote_addr
        print(ip_addr)
        return jsonify(get_video_and_ratings(g.db, video_id, ip_addr))

    @app.get('/video-count')
    def get_video_count():
        player = request.args.get('player', None)
        return jsonify(get_vid_count(g.db, player))

    @app.post('/rating')
    def post_rating():
        rating = request.form.get('rating')
        player = request.form.get('player')
        video = request.form.get('video')
        ip_address = request.remote_addr
        return jsonify(submit_rating(g.db, ip_address=ip_address, video=video, player=player, rating=rating))
    
    return app
