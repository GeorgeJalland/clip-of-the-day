from flask import Flask, Blueprint, request, g, jsonify, send_from_directory, Response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os

from app.db import SessionLocal, create_schema, submit_rating, get_players_with_ratings, get_video_and_ratings, get_vid_count, get_all_videos
from common.config import Config

def create_app(config_class=Config):

    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    app.config.from_object(config_class)

    CORS(app, origins=['http://localhost:*'])

    api = Blueprint("api", __name__, url_prefix="/api")

    with app.app_context():
        create_schema()

    @app.before_request
    def create_session():
        g.db = SessionLocal()

    @app.teardown_request
    def remove_session(error=None):
        SessionLocal.remove()

    @api.get('/players')
    def get_players():
        return jsonify(get_players_with_ratings(g.db))

    @api.get('/video/<int:desired_position>')
    def get_video(desired_position: int):
        player_id = request.args.get('player', None)
        ip_addr = request.remote_addr
        return jsonify(get_video_and_ratings(g.db, "position", desired_position, ip_addr, player_id))

    @api.get('/video/id/<int:id>')
    def get_video_by_id(id: int):
        player_id = request.args.get('player', None)
        ip_addr = request.remote_addr
        return jsonify(get_video_and_ratings(g.db, "id", id, ip_addr, player_id))

    @api.get('/video-count')
    def get_video_count():
        player_id = request.args.get('player', None)
        return jsonify(get_vid_count(g.db, player_id))

    @api.post('/rating')
    def post_rating():
        data = request.get_json()
        rating = data.get('rating')
        videoId = data.get('videoId')
        ip_address = request.remote_addr
        return jsonify(submit_rating(g.db, ip_address=ip_address, videoId=videoId, rating=rating))
    
    @api.route("/videos/<path:filepath>")
    def serve_videos(filepath):
        return send_from_directory(app.config.get("VIDEO_DIRECTORY"), filepath)

    @api.get("/sitemap.xml")
    def sitemap():
        base_url = "https://clipoftheday.io/rocket-league"
        lastmod = "2025-04-13"
        sitemap_items = ""

        videos = get_all_videos(g.db)

        for video in videos:
            loc = f"{base_url}/clip/{video.id}"
            sitemap_items += f"""
            <url>
                <loc>{loc}</loc>
                <lastmod>{lastmod}</lastmod>
            </url>"""

        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            {sitemap_items}
        </urlset>"""

        return Response(xml_content, mimetype="application/xml")
    
    @app.route('/')
    def index():
        return send_from_directory(app.root_path, "static/index.html")

    @app.route('/<path:filename>')
    def static_files(filename):
        static_dir = os.path.join(app.root_path, 'static')
        file_path = os.path.join(static_dir, filename)

        if os.path.isfile(file_path):
            return send_from_directory(static_dir, filename)
        else:
            return index()

    app.register_blueprint(api)
    
    return app
