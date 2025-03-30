from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy import func, case
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

def get_players_with_ratings(session: Session, game):
    # needs reworking
    # cache for 1 minute?
    results = (
        session.query(
            Player.name,
            func.sum(Rating.rating).label("sum_ratings"),
            func.avg(Rating.rating).label("average_rating")
        )
        .outerjoin(Player.videos)   # Join videos associated with the player
        .outerjoin(Video.ratings)   # Join ratings associated with the video
        .group_by(Player.id)        # Group by player to aggregate ratings
        .all()
    )
    return [{'player': row[0], 'sum_ratings': row[1], 'avg_rating': row[2]} for row in results]

def get_vid_count(session: Session, player: str) -> dict:
    query = session.query(Video).join(Video.player)
    if player:
        query = query.filter(Player.name == player)
    return query.count()
  
def get_video_and_ratings(session: Session, index: int, ip_address: str) -> dict:
    user_rating = func.max(
            case(
                (Rating.ip_address == ip_address, Rating.rating),
                else_=None
        ),
    ).label("user_rating")

    result = (
        session.query(
            Video.id,
            Video.name,
            Video.subdir_and_filename,
            Player.name.label("player_name"),
            func.coalesce(func.sum(Rating.rating), 0).label("total_rating"),
            func.coalesce(func.avg(Rating.rating), 0).label("average_rating"),
            user_rating,
        )
        .outerjoin(Rating, Video.id == Rating.video_id)
        .join(Player, Video.player_id == Player.id)
        .filter(Video.id >= index)
        .group_by(Video.id, Video.name, Video.full_path, Player.name)
        .limit(1)
        .first()
    )

    return {"id": result[0], "video_name": result[1], "path": result[2], "player": result[3], "total_rating": result[4], "avg_rating": result[5], "user_rating": result[6]}
