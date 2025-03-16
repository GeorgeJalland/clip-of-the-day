from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from common.config import Config
from common.db_models import Base, Video, Rating

logger = logging.getLogger(__name__)

db = create_engine(Config.SQLALCHEMY_DATABASE_URI)

def create_schema():
    Base.metadata.create_all(db)

def submit_rating(db, ip_address, video, player, rating):
    with Session(db) as session:
        existing_rating = session.query(Rating).filter_by(ip_address=ip_address, video=video, player=player).one_or_none()
        if existing_rating:
            existing_rating.rating = rating
        else:
            new_rating = Rating(ip_address=ip_address, video=video, player=player, rating=rating)
            session.add(new_rating)
        session.commit()

def get_ratings_for_video(db, video):
    # return dictionary of sum ratings, ratings count, avg rating
    pass

def get_ratings_by_player(db, game):
    # needs reworking
    with Session(db) as session:
        # cache for 1 minute?
        result = session.query(
            Rating.player,
            func.sum(Rating.rating),
            func.avg(Rating.rating)
        ).filter(Rating.video.contains(game)).group_by(Rating.player).all()
        return [{'player': row[0], 'sum_ratings': row[1], 'avg_rating': row[2]} for row in result]

def get_user_video_rating(db, video, ip_address) -> int:
    # return the rating of a given video for given ip_address
    pass

def get_all_videos(db):
    with Session(db) as session:
        vids = session.query(Video).all()
    return vids

def get_video_count(db):
    with Session(db) as session:
        return session.query(Video).count()

def get_next_video_and_ratings(db, index):
    with Session(db) as session:
        # redo this using subquery in select
        subquery = session.query(Video).filter(Video.id > index).limit(1).subquery()
        result = session.query(
            Video.id,
            Video.name,
            func.sum(Rating.rating),
            func.avg(Rating.rating)
            ).filter(Rating.video_id == subquery.c.id).join(subquery).all()
        return result


def get_random_video_and_ratings(db):
    pass


def get_all_players_and_ratings(db):
    pass