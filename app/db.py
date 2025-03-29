from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy import func
import logging

from common.config import Config
from common.db_models import Base, Video, Rating, Player

logger = logging.getLogger(__name__)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

SessionLocal = scoped_session(sessionmaker(bind=engine))

def create_schema():
    Base.metadata.create_all(engine)

def submit_rating(session: Session, ip_address, video, player, rating):
    existing_rating = session.query(Rating).filter_by(ip_address=ip_address, video=video, player=player).one_or_none()
    if existing_rating:
        existing_rating.rating = rating
    else:
        new_rating = Rating(ip_address=ip_address, video=video, player=player, rating=rating)
        session.add(new_rating)
    session.commit()

def get_ratings_for_video(session: Session, video):
    # return dictionary of sum ratings, ratings count, avg rating
    pass
    # with Session(db) as session:
    #     session.query()

def get_ratings_by_player(session: Session, game):
    # needs reworking
    # cache for 1 minute?
    result = session.query(
        Rating.player,
        func.sum(Rating.rating),
        func.avg(Rating.rating)
    ).filter(Rating.video.contains(game)).group_by(Rating.player).all()
    return [{'player': row[0], 'sum_ratings': row[1], 'avg_rating': row[2]} for row in result]

def get_user_video_rating(session: Session, video, ip_address) -> int:
    # return the rating of a given video for given ip_address
    pass

def get_all_videos(session: Session):
    vids = session.query(Video).all()
    return vids

def get_video_count(session: Session):
    return session.query(Video).count()
  
def get_video_and_ratings(session: Session, index):
    result = session.query(
            Video.id,
            Video.subdir_and_filename,
            Player.name,
            func.coalesce(func.sum(Rating.rating), 0).label("total_rating"),
            func.coalesce(func.avg(Rating.rating), 0).label("average_rating")
        ).outerjoin(Rating, Video.id == Rating.video_id) \
        .join(Player, Video.player_id == Player.id) \
        .filter(Video.id >= index) \
        .group_by(Video.id, Video.name) \
        .limit(1) \
        .all()
    return result[0]

def get_random_video_and_ratings(session: Session):
    pass

def get_all_players_and_ratings(session: Session):
    pass