from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy import func, case, desc, over
import logging

from common.config import Config
from common.db_models import Base, Video, Rating, Player

logger = logging.getLogger(__name__)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

SessionLocal = scoped_session(sessionmaker(bind=engine))

def create_schema():
    Base.metadata.create_all(engine)

def submit_rating(session: Session, ip_address, videoId, rating):
    # When foreign key constaint error, return something meaningful?
    existing_rating = session.query(Rating).filter_by(ip_address=ip_address, video_id=videoId).one_or_none()
    if existing_rating:
        existing_rating.rating = rating
    else:
        new_rating = Rating(ip_address=ip_address, video_id=videoId, rating=rating)
        session.add(new_rating)
    session.commit()

def get_players_with_ratings(session: Session) -> list:
    result = (
        session.query(
            Player.name,
            Player.id,
            func.sum(Rating.rating).label("sum_ratings"),
        )
        .outerjoin(Player.videos)
        .outerjoin(Video.ratings)
        .group_by(Player.id)
        .all()
    )

    return [row._asdict() for row in result] if result else []

def get_vid_count(session: Session, player_id: int) -> dict:
    query = session.query(Video).join(Video.player)
    if player_id:
        query = query.filter(Player.id == player_id)
    return query.count()
  
def get_video_and_ratings(session: Session, desired_position: int, ip_address: str, player_id: int | None = None) -> dict:
    user_rating = func.max(
            case(
                (Rating.ip_address == ip_address, Rating.rating),
                else_=None
        ),
    ).label("user_rating")

    position = over(
        func.row_number(),
        order_by=desc(Video.name)
    ).label('position')

    subq = (
        session.query(
            position,
            Video.id,
            Video.name,
            Video.subdir_and_filename.label("path"),
            Player.name.label("player_name"),
            func.coalesce(func.sum(Rating.rating), 0).label("total_rating"),
            func.coalesce(func.avg(Rating.rating), 0).label("average_rating"),
            user_rating,
        )
        .outerjoin(Rating, Video.id == Rating.video_id)
        .join(Player, Video.player_id == Player.id)
    )

    if player_id is not None:
        subq = subq.filter(Player.id == player_id)

    subq = subq.group_by(Video.id).subquery()

    query = session.query(subq).filter(subq.c.position == desired_position)

    result = query.first()

    return result._asdict() if result else None
