# from flask_restful import Resource
# from application.models import Songs,User_likes_ratings,Users,Albums,Playlists,Playlist_songs,UserActivity
# from application.database import db

# class SongsAPI(Resource):
#     def get(self):
#         trend = Songs.query.order_by(Songs.song_views.desc()).limit(4)
#         songs = [[song.song_id, song.song_name] for song in Songs.query.all()]
#         trend = [[song.song_id, song.song_name] for song in trend]
#         albums = [[album.album_id, album.album_name] for album in Albums.query.all()]
#         return json.dumps({'songs': songs, 'albums': albums,'trend':trend})
    
#     def get(self,song_id):
#         song = Songs.query.filter(Songs.song_id == song_id).first()
#         album = Albums.query.filter(Albums.album_id == song.album_id).first()
#         song.song_views += 1
#         db.session.commit() 
#         song_to_send =  dict()
#         song_to_send['name'] = song.song_name
#         song_to_send['lyrics'] = song.lyrics
#         song_to_send['artist'] = album.artist
#         song_to_send['duration'] = song.duration
#         song_to_send['img'] = str(song.album.image_blob.decode('utf-8', 'ignore'))
#         song_to_send['song'] = str(song.music_blob.decode('utf-8', 'ignore'))
#         return json.dumps(song_to_send)
    
#     def put(self,song_id):
#         song_name = request.form['song-name']
#         lyrics = request.form['lyrics']
#         duration = request.form['duration']
#         song = Songs.query.filter(Songs.song_id == song_id).first()
#         song.song_name = song_name
#         song.lyrics = lyrics
#         song.duration = duration
#         db.session.commit()
#         return redirect("/creator") 
      
#     def delete(self,song_id):
#         playlists = Playlist_songs.query.filter(Playlist_songs.song_id == song_id)
#         try:
#             if len(playlists.all()) != 0:
#                 playlists.delete()
#             Songs.query.filter(Songs.song_id == song_id).delete()
#             db.session.commit()
#             return "200"
#         except:
#             db.session.rollback()
#             return "403" 
#     def post(self):
#         pass

# class AlbumAPI(Resource):
#     def get(self,album_id):
#         album = Albums.query.filter(Albums.album_id == album_id).first()
#         songs = Songs.query.filter(Songs.album_id == album.album_id).all()
#         songs_list = []
#         for song in songs:
#             song_to_send =  dict()
#             song_to_send['name'] = song.song_name
#             song_to_send['lyrics'] = song.lyrics
#             song_to_send['artist'] = album.artist
#             song_to_send['duration'] = song.duration
#             song_to_send['img'] = str(song.album.image_blob.decode('utf-8', 'ignore'))
#             song_to_send['song'] = str(song.music_blob.decode('utf-8', 'ignore'))
#             songs_list.append(song_to_send)
#         return json.dumps({'songs':songs_list})
#     def put(self):
#         pass
#     def delete(self,album_id):
#         album_c = Albums.query.filter(Albums.album_id == album_id)
#         album = album_c.first()
#         songs = Songs.query.filter(Songs.album_id == album.album_id).all()
#         for song in songs:
#             playlists = Playlist_songs.query.filter(Playlist_songs.song_id == song.song_id)
#             if len(playlists.all()) != 0:
#                 playlists.delete()
#             Songs.query.filter(Songs.song_id == song.song_id).delete()
#         album_c.delete()
#         db.session.commit()
#         return "200"
#     def post(self):
#         pass

