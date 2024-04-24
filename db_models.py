from sqlalchemy import Column, DateTime, CheckConstraint, UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    added_time = Column(DateTime, default=datetime.now)
    modified_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

db = SQLAlchemy(model_class=Base)

class Ratings(db.Model):
    id = db.Column((db.Integer), primary_key=True)
    ip_address = db.Column(db.String(15), nullable=False)
    video = db.Column(db.String(50), nullable=False)
    rating = db.Column((db.Integer), nullable=False)
    __table_args__ = (UniqueConstraint('ip_address', 'video', name='cant_rate_vid_twice'),
                      CheckConstraint("1 <=  rating <= 5"),)
    
    def __repr__(self) -> str:
        return f'<Rating {self.content}>'
