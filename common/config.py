import os

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(basedir)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(project_root, 'instance/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VIDEO_DIRECTORY = os.getenv('VIDEO_DIRECTORY')
    THUMBNAIL_DIRECTORY_NAME = "thumbnails"
