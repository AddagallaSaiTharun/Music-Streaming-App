import os

cur_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(cur_dir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class localConfig(Config):
    SQLITE_DB_DIR = os.path.join(cur_dir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "app.db")
    DEBUG = True