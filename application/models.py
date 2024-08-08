import uuid
from datetime import datetime
from sqlalchemy import func
from application.database import db


class Albums(db.Model): 
    _tablename_="albums"    
    album_id = db.Column(db.String, primary_key=True)
    album_name = db.Column(db.String(50), nullable=False,unique=True)
    album_owner_id = db.Column(db.String,db.ForeignKey('users.user_id'), nullable=False)
    image_blob=db.Column(db.BLOB,nullable=False,unique=True)
    album_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    artist = db.Column(db.String)
    songs_in = db.relationship("Songs",backref="album")

class Playlists(db.Model):
    _tablename_="playlists"
    playlist_id = db.Column(db.String, primary_key=True)
    playlist_name = db.Column(db.String(50), nullable=False)
    playlist_owner_id = db.Column(db.String,db.ForeignKey('users.user_id'), nullable=False)
    songs_in = db.relationship("Songs",secondary="playlist_songs",backref="song_playlists")

class Playlist_songs(db.Model):  #Secondary Table
    _tablename_="playlist_songs"
    song_id=db.Column(db.String,db.ForeignKey("songs.song_id"),primary_key=True,nullable=False)
    playlist_id=db.Column(db.String,db.ForeignKey("playlists.playlist_id"),primary_key=True,nullable=False)

class Songs(db.Model): 
    _tablename_="songs"
    song_id = db.Column(db.String, primary_key=True)
    song_name = db.Column(db.String(50), nullable=False,unique=True)
    album_id = db.Column(db.String, db.ForeignKey('albums.album_id'),nullable=False)
    duration=db.Column(db.Integer,nullable=False)
    genre=db.Column(db.String(50),nullable=False)
    lyrics = db.Column(db.String,nullable=False)
    song_views=db.Column(db.Integer,server_default=db.text('0'))
    liked=db.Column(db.Integer,server_default=db.text('0'))
    song_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    music_blob=db.Column(db.BLOB,nullable=False,unique=True)
    # song_img=db.Column(db.BLOB,nullable=False,unique=True)

class Users(db.Model):
    _tablename_="users"
    user_id = db.Column(db.String,primary_key = True)
    user_name = db.Column(db.String(50),nullable=False,unique=True)
    role= db.Column(db.String(50),nullable=False)
    password = db.Column(db.String,nullable=False)

class User_likes_ratings(db.Model):
    _tablename_="user_likes_ratings"
    user_id=db.Column(db.String,db.ForeignKey('users.user_id'),primary_key = True,nullable=False)
    song_id=db.Column(db.String,db.ForeignKey('songs.song_id'),primary_key=True,nullable=False)
    song_liked=db.Column(db.Integer,server_default=db.text('0'))
    song_rate=db.Column(db.Float,server_default=db.text('0'))

class UserActivity(db.Model):
    _tablename_ = "User_activity"
    entry_id = db.Column("entry", db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_ID = db.Column("user_id", db.String)
    date = db.Column("login_date", db.DateTime, default=func.now())


def add_user_login(user_ID, date=None):
    entry = UserActivity(user_ID=user_ID, date=date)
    db.session.add(entry)
    db.session.commit()