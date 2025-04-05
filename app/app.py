from flask import Flask, Blueprint, request, g, jsonify, send_from_directory
from flask_cors import CORS
from urllib.parse import quote

from app.db import SessionLocal, create_schema, submit_rating, get_players_with_ratings, get_video_and_ratings, get_vid_count, get_max_vid_id
from common.config import Config

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app, origins=['http://localhost:*'])

    api = Blueprint("api", __name__, url_prefix="/api")

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

    @api.get('/players')
    def get_players():
        # need to remove concept of game, make it rocket league only?
        game = request.args.get('game', GAMES[0])
        return jsonify(get_players_with_ratings(g.db, game))

    @api.get('/video/<int:video_id>')
    def get_video(video_id: int):
        # add default value for video_id which is random ?
        action = request.args.get('action', 'next')
        player_id = request.args.get('player', None)
        ip_addr = request.remote_addr
        return jsonify(get_video_and_ratings(g.db, video_id, ip_addr, player_id, action))

    @api.get('/video-count')
    def get_video_count():
        # Should this return max video id as opposed to count? or extra endpoint?
        player_id = request.args.get('player', None)
        return jsonify(get_vid_count(g.db, player_id))

    @api.get('/max-quote-id')
    def get_max_video_id():
        return jsonify(get_max_vid_id(g.db))

    @api.post('/rating')
    def post_rating():
        rating = request.form.get('rating')
        player = request.form.get('player')
        video = request.form.get('video')
        ip_address = request.remote_addr
        return jsonify(submit_rating(g.db, ip_address=ip_address, video=video, player=player, rating=rating))
    
    @api.route("/videos/<path:filepath>")
    def serve_videos(filepath):
        return send_from_directory(app.config.get("VIDEO_DIRECTORY"), filepath)
    
    app.register_blueprint(api)
    
    return app
