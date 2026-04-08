import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'moodle-leband-dev-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'moodle.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER_SLIDES = os.path.join(BASE_DIR, 'static', 'uploads', 'slides')
    UPLOAD_FOLDER_SUBMISSIONS = os.path.join(BASE_DIR, 'static', 'uploads', 'submissions')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
