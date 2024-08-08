import uuid
import json
from flask import render_template, request, make_response, redirect
from application.database import db
from werkzeug.security import generate_password_hash,check_password_hash
from io import BytesIO
from flask import current_app as app
from application.models import Songs,User_likes_ratings,Users,Albums,Playlists,Playlist_songs,UserActivity
import time
from sqlalchemy import func
import jwt
import base64


def gen_uuid():
    return str(uuid.uuid4())

def add_user_login(user_ID, date=None):
    entry = UserActivity(user_ID=user_ID, date=date)
    db.session.add(entry)
    db.session.commit()

def check_cookie(req):
    """
    Checks if a cookie exists in the request and decodes it if it does.

    Args:
        req: The Flask request object.

    Returns:
        A dictionary containing user information from the decoded cookie,
        or a default dictionary with "none" values if no cookie is found.
    """
    if req.cookies and req.cookies.get("token") :
        return jwt.decode(req.cookies.get("token"),app.config['SECRET_KEY'], algorithms='HS256')
    return {"username":"none","user_id":"none","role":"user","loggedIn": 0}




#all apis used
@app.route('/liked_song/<string:song_id>',methods=['GET'])
def like(song_id):
    """
    Handles liking a song.

    This function checks if the user is logged in, retrieves the user's ID,
    and updates the User_likes_ratings table to reflect the like.

    Args:
        song_id: The ID of the song being liked.

    Returns:
        "1" if the like operation was successful, "0" otherwise.
    """
    cookie = check_cookie(request)
    if cookie['username'] is None or cookie['username'] == 'none':
        return "0"

    user = Users.query.filter(Users.user_name == cookie['username']).first()
    if user is None:
        return "0"

    user_id = user.user_id
    like_record = User_likes_ratings.query.filter(User_likes_ratings.song_id == song_id,User_likes_ratings.user_id == user_id).first()
    if like_record:
        like_record.song_liked = 1
        db.session.commit()
    else:
        new_like_record = User_likes_ratings(user_id=user_id,song_id=song_id,song_liked=1)
        db.session.add(new_like_record)
        db.session.commit()
    return '1'

@app.route('/disliked_song/<string:song_id>',methods=['GET'])
def dislike(song_id):
    """
    Handles disliking a song.

    This function checks if the user is logged in, retrieves the user's ID,
    and updates the User_likes_ratings table to reflect the dislike.

    Args:
        song_id: The ID of the song being disliked.

    Returns:
        "1" if the dislike operation was successful, "0" otherwise.
    """
    cookie = check_cookie(request)
    if cookie['username'] is None or cookie['username'] == 'none':
        return "0"

    user = Users.query.filter(Users.user_name == cookie['username']).first()
    if user is None:
        return "0"

    user_id = user.user_id
    like_record = User_likes_ratings.query.filter_by(user_id=user_id, song_id=song_id).first()

    if like_record:
        like_record.song_liked = 0
        like_record.song_rate = 0 
        db.session.commit()
    else:
        new_like_record = User_likes_ratings(user_id=user_id, song_id=song_id, song_liked=0)
        db.session.add(new_like_record)
        db.session.commit()
    return '1'

@app.route('/song_liked/<string:song_id>',methods=['GET'])
def get_rate(song_id):
    """
    Retrieves the like status of a song for the current user.

    Args:
        song_id: The ID of the song.

    Returns:
        "1" if the song is liked, "0" otherwise.
    """
    user_cookie = check_cookie(request)
    if user_cookie['username'] is None or user_cookie['username'] == 'none':
        return "0"

    user = Users.query.filter(Users.user_name == user_cookie['username']).first()
    if user is None:
        return "0"

    user_id = user.user_id
    like_record = User_likes_ratings.query.filter_by(user_id=user_id, song_id=song_id).first()

    if like_record:
        return str(like_record.song_liked)
    return '0'


@app.route('/rating/<string:song_id>',methods=['POST'])
def rate(song_id):
    """
    Handles song rating requests.

    This function retrieves the user's information from the cookie,
    updates the rating for the specified song in the database,
    and redirects to the home page.

    Args:
        song_id: The ID of the song being rated.

    Returns:
        - Redirects to the home page ("/") if the rating is successful.
        - Returns "0" if the user is not logged in.
    """
    user_cookie = check_cookie(request)
    if user_cookie['username'] is None or user_cookie['username'] == 'none':
        return "0"
    rating = request.form['stars']
    user = Users.query.filter(Users.user_name == user_cookie['username']).first()
    user_rating = User_likes_ratings.query.filter_by(user_id=user.user_id, song_id=song_id).first()
    if user_rating:
        user_rating.song_rate = rating
    else:
        user_rating = User_likes_ratings(user_id=user.user_id, song_id=song_id, song_rate=rating)
        db.session.add(user_rating)
    db.session.commit()
    return redirect('/')

@app.route('/save_changes/<string:song_id>',methods=['POST'])
def save_songs(song_id):
    """
    Updates song details based on user input.

    This function handles POST requests to update song information.
    It retrieves the song details from the request form, updates the corresponding song in the database,
    and redirects to the creator page.

    Args:
        song_id: The unique identifier of the song to be updated.

    Returns:
        A redirect response to the "/creator" route.
    """
    if request.method == 'POST':
        updated_song_name = request.form['song-name']
        updated_lyrics = request.form['lyrics']
        updated_duration = request.form['duration']
        song = Songs.query.filter(Songs.song_id == song_id).first()
        song.song_name = updated_song_name
        song.lyrics = updated_lyrics
        song.duration = updated_duration
        db.session.commit()
        return redirect("/creator")
       
@app.route('/deletealbum/<string:album_id>')
def delete_album(album_id):
    """
    Deletes an album and its associated songs from the database.

    This function handles the deletion of an album and all its associated songs.
    It first retrieves the album and its songs based on the provided album ID.
    Then, it iterates through the songs, deleting any playlist entries associated with them.
    Finally, it deletes the songs and the album itself from the database.

    Args:
        album_id: The unique identifier of the album to be deleted.

    Returns:
        "200" if the deletion was successful, indicating a successful HTTP status code.
    """
    album_query = Albums.query.filter(Albums.album_id == album_id)
    album = album_query.first()
    if album:
        songs = Songs.query.filter(Songs.album_id == album.album_id).all()
        for song in songs:
            playlist_entries = Playlist_songs.query.filter(Playlist_songs.song_id == song.song_id)
            if playlist_entries.count() > 0:
                playlist_entries.delete()
            Songs.query.filter(Songs.song_id == song.song_id).delete()

        album_query.delete()
        db.session.commit()
        return "200"
    return "Album not found", 404


@app.route('/delete_song/<string:song_id>')
def delete_song(song_id):
    """
    Deletes a song from the database and associated playlist entries.

    This function handles the deletion of a song and its associated entries in the Playlist_songs table.
    It first retrieves all playlist entries associated with the song.
    If there are any entries, they are deleted.
    Then, the song itself is deleted from the Songs table.

    Args:
        song_id: The unique identifier of the song to be deleted.

    Returns:
        "200" if the deletion was successful, indicating a successful HTTP status code.
        "403" if an error occurred during the deletion process.
    """
    playlist_entries = Playlist_songs.query.filter(Playlist_songs.song_id == song_id)

    try:
        if playlist_entries.count() > 0:
            playlist_entries.delete()
        Songs.query.filter(Songs.song_id == song_id).delete()
        db.session.commit()
        return "200"
    except:
        db.session.rollback()
        return "403"



@app.route("/add_song_queue/<string:song_name>")
def add_song_queue(song_name):
    """
    Adds a song to the queue and increments its view count.

    This function retrieves a song by its name, increments its view count,
    and returns a JSON representation of the song's details.

    Args:
        song_name: The name of the song to be added to the queue.

    Returns:
        A JSON object containing the song's details.
    """
    song = Songs.query.filter(Songs.song_name == song_name).first()
    if song:
        album = Albums.query.filter(Albums.album_id == song.album_id).first()
        song.song_views += 1
        db.session.commit()
        song_data = {
            'name': song.song_name,
            'lyrics': song.lyrics,
            'artist': album.artist,
            'duration': song.duration,
            'img': str(song.album.image_blob.decode('utf-8', 'ignore')),
            'song': str(song.music_blob.decode('utf-8', 'ignore'))
        }
        return json.dumps(song_data)
    else:
        return "Song not found", 404


@app.route('/newplaylist/<string:playlist_name>')
def newplaylist(playlist_name):
    """
    Creates a new playlist for the current user.

    This function handles requests to create a new playlist. It retrieves the current user's information
    from the cookie, creates a new playlist object, and attempts to add it to the database.

    Args:
        playlist_name: The name of the new playlist.

    Returns:
        "200" if the playlist creation was successful, "403" if an error occurred.
    """
    current_user = Users.query.filter(Users.user_name == request.cookies.get("username")).first()
    new_playlist = Playlists(playlist_id=gen_uuid(), playlist_name=playlist_name, playlist_owner_id=current_user.user_id)

    try:
        db.session.add(new_playlist)
        db.session.commit()
        return "200"  
    except:
        db.session.rollback()
        return "403" 


@app.route('/addplaylist/<string:playlist_name>/<string:song_name>')
def add_song_to_playlist(playlist_name, song_name):
    """
    Adds a song to an existing playlist.

    This function retrieves the playlist ID based on the provided playlist name,
    finds the song by its name, and creates a new Playlist_songs entry to link them.

    Args:
        playlist_name: The name of the playlist to add the song to.
        song_name: The name of the song to add to the playlist.

    Returns:
        "200" if the song was successfully added to the playlist, "403" if an error occurred.
    """
    playlist = Playlists.query.filter(Playlists.playlist_name == playlist_name).first()
    if playlist:
        song = Songs.query.filter(Songs.song_name == song_name).first()
        if song:
            playlist_song = Playlist_songs(song_id=song.song_id, playlist_id=playlist.playlist_id)
            try:
                db.session.add(playlist_song)
                db.session.commit()
                return "200"
            except:
                db.session.rollback()
                return "403"
        return "Song not found", 404
    return "Playlist not found", 404


@app.route('/getnames', methods=['GET'])
def get_names():
    """
    Retrieves and returns a JSON representation of song and album names.

    This function retrieves the following data from the database:
    - All song IDs and names
    - Top 4 trending songs (based on song views)
    - All album IDs and names

    The data is then formatted into a JSON structure and returned as a response.

    Returns:
        A JSON object containing lists of song and album names.
    """
    trending_songs = Songs.query.order_by(Songs.song_views.desc()).limit(4)
    all_songs = [[song.song_id, song.song_name] for song in Songs.query.all()]
    trending_songs_data = [[song.song_id, song.song_name] for song in trending_songs]
    all_albums = [[album.album_id, album.album_name] for album in Albums.query.all()]

    return json.dumps({'songs': all_songs, 'albums': all_albums, 'trend': trending_songs_data})


#all routes
@app.route('/album_details/<string:album_name>', methods=['GET'])
def find_album(album_name):
    """
    Retrieves and returns details of songs in a specific album.

    This function handles GET requests to the "/album_details/<album_name>" route.
    It retrieves the album and its associated songs based on the provided album name.
    The song details are then formatted into a JSON structure and returned as a response.

    Args:
        album_name: The name of the album to retrieve songs from.

    Returns:
        A JSON object containing a list of song details.
    """
    album = Albums.query.filter(Albums.album_name == album_name).first()
    if album:
        songs = Songs.query.filter(Songs.album_id == album.album_id).all()
        song_details = []
        for song in songs:
            song_data = {
                'name': song.song_name,
                'lyrics': song.lyrics,
                'artist': album.artist,
                'duration': song.duration,
                'img': str(song.album.image_blob.decode('utf-8', 'ignore')),
                'song': str(song.music_blob.decode('utf-8', 'ignore'))
            }
            song_details.append(song_data)
        return json.dumps({'songs': song_details})
    return "Album not found", 404

@app.route('/song/<string:song_id>',methods=['GET'])
def showsong(song_id):
    """
    Displays details of a specific song.

    This function handles GET requests to the "/song/<song_id>" route.
    It retrieves the song details and the creator's username based on the provided song ID.

    Args:
        song_id: The unique identifier of the song.

    Returns:
        - Renders the "songs.html" template with the song details and creator's username.
    """
    if request.method == 'GET':
        song = Songs.query.filter(Songs.song_id==song_id).first()
        if song:
            user = Users.query.filter(Users.user_id == song.album.album_owner_id).first()
            return render_template('songs.html',song=song,username=user.user_name)
        return "Song not found", 404

@app.route('/album/<string:album_id>',methods=['GET'])
def showalbum(album_id):
    """
    Displays details of a specific album.

    This function handles GET requests to the "/album/<album_id>" route.
    It retrieves the album details, its songs, and the creator's username based on the provided album ID.

    Args:
        album_id: The unique identifier of the album.

    Returns:
        - Renders the "album.html" template with the album details, songs, and creator's username.
    """
    if request.method == 'GET':
        cookie = check_cookie(request)
        album = Albums.query.filter(Albums.album_id==album_id).first()
        if album:
            songs = Songs.query.filter(Songs.album_id == album_id).all()
            user = Users.query.filter(Users.user_id == album.album_owner_id).first()
            data = {
                'name': album.album_name,
                'artist': user.user_name,
                'count': len(songs),
                'songs': [
                    {
                        'name': song.song_name,
                        'duration': time.strftime("%M:%S", time.gmtime(song.duration)),
                        'genre': song.genre,
                        'views': song.song_views,
                        'author': song.album.artist
                    } for song in songs
                ]
            }
            return render_template("album.html",username=cookie.get('username'),album=data,image_blob=album.image_blob)
        return "Album not found", 404 


@app.route('/playlist/<string:playlist_id>',methods=['GET'])
def playlist1(playlist_id):
    """
    Displays details of a specific playlist.

    This function handles GET requests to the "/playlist/<playlist_id>" route.
    It retrieves the playlist details, its songs, and the creator's username based on the provided playlist ID.

    Args:
        playlist_id: The unique identifier of the playlist.

    Returns:
        - Renders the "playlist.html" template with the playlist details, songs, and creator's username.
    """
    if request.method == 'GET':
        playlist_songs = Playlist_songs.query.filter(Playlist_songs.playlist_id == playlist_id).all()
        playlist = Playlists.query.filter(Playlists.playlist_id == playlist_id).first()
        if playlist:
            playlist_owner = Users.query.filter(Users.user_id == playlist.playlist_owner_id).first()
            playlist_data = {
                'name': playlist.playlist_name,
                'artist': playlist_owner.user_name,
                'count': len(playlist_songs),
                'songs': []
            }
            for playlist_song in playlist_songs:
                song = Songs.query.filter(Songs.song_id == playlist_song.song_id).first()
                if song:
                    album = Albums.query.filter(Albums.album_id == song.album_id).first()
                    if album:
                        song_data = {
                            'name': song.song_name,
                            'duration': time.strftime("%M:%S", time.gmtime(song.duration)),
                            'genre': song.genre,
                            'views': song.song_views,
                            'author': album.artist
                        }
                        playlist_data['songs'].append(song_data)
            cookie = check_cookie(request)
            return render_template("playlist.html", username=cookie.get('username'), album=playlist_data)
        return "Playlist not found", 404


@app.route('/admin/allcreator', methods=['GET'])
def all_creators():
    """
    Retrieves and displays data for all creators and their albums.

    This function handles GET requests to the "/admin/allcreator" route.
    It retrieves data for all creators and their albums, including:
    - Total number of creators
    - List of creators with their albums and songs

    Returns:
        - Renders the "admin_file.html" template with the retrieved data.
        - Redirects to the "/admin" route if the user is not an admin.
    """
    if request.method == 'GET':
        cookie = check_cookie(request)
        user_id = cookie.get("user_id")
        user = Users.query.filter(Users.user_id == user_id).first()
        if user is None or user.role != 'admin':
            return redirect("/admin")
        creators = Users.query.filter(Users.role == 'creator').all()
        all_users_data = {'count': len(creators), 'users': []}
        for creator in creators:
            user_data = {'name': creator.user_name, 'albums': {'count': 0, 'album': []}}
            albums = Albums.query.filter(Albums.album_owner_id == creator.user_id).order_by(Albums.album_name.asc()).all()
            user_data['albums']['count'] = len(albums)
            for album in albums:
                songs = Songs.query.filter(Songs.album_id == album.album_id).order_by(Songs.song_name.asc()).all()
                album_data = {'id': album.album_id, 'name': album.album_name, 'songs': {'count': len(songs), 'song': []}}
                for song in songs:
                    song_data = {
                        'name': song.song_name,
                        'views': song.song_views,
                        'duration': song.duration,
                        'genre': song.genre,
                        'liked': song.liked,
                        'lyrics': song.lyrics,
                        'id': song.song_id
                    }
                    album_data['songs']['song'].append(song_data)
                user_data['albums']['album'].append(album_data)
            all_users_data['users'].append(user_data)
        return render_template('admin_file.html', all_users_data=all_users_data, username=cookie.get("username"))

@app.route('/admin/view', methods=['GET'])
def admin_view():
    """
    Renders the admin dashboard with user statistics and activity data.

    This function handles GET requests to the "/admin/view" route.
    It retrieves various statistics and activity data from the database,
    including:

    - Total number of users
    - Total number of creators
    - Total number of songs
    - Total number of albums
    - Daily unique user login counts

    The function then renders the "admin.index.html" template with the retrieved data.

    Returns:
        - Renders the "admin.index.html" template with the admin dashboard data.
        - Redirects to the "/admin" route if the user is not an admin.
    """
    if request.method == 'GET':
        cookie = check_cookie(request)
        user_id = cookie.get("user_id")
        user = Users.query.filter(Users.user_id == user_id).first()
        if user is None or user.role != 'admin':
            return redirect("/admin")
        else:
            user_query = Users.query
            tu = user_query.filter(Users.role != "admin").count()
            tc = user_query.filter(Users.role == "creator").count()
            ts = Songs.query.count()
            ta = Albums.query.count()
            result = db.session.query(func.date(UserActivity.date).label('login_date'),func.count(func.distinct(UserActivity.user_ID)).label('unique_user_count')).group_by(func.date(UserActivity.date)).all()
            res = []
            for row in result:
                tdate, tmonth, tyear = row.login_date.split("-")
                tyear = tyear.split()[0]
                res.append([tdate, tmonth, tyear, row.unique_user_count])
            return render_template("admin.index.html", tu=tu, tc=tc, ts=ts, ta=ta,username=cookie.get("username"), result=res)
        
@app.route("/admin", methods=['GET', 'POST'])
@app.route("/admin/signin", methods=['GET', 'POST'])
def admin_signin():
    """
    Handles admin signin requests.

    This function processes both GET and POST requests to the "/admin" and "/admin/signin" routes.
    It handles admin login, sets cookies, and generates a JWT token for authentication.

    Returns:
        - Renders the "admin.signin.html" template if it's a GET request.
        - Redirects to the "/admin/view" route with a success flag and sets cookies if login is successful.
        - Renders the "admin.signin.html" template with error flags if login fails:
            - flag=-2: User not found
            - flag=-3: Incorrect password
            - flag=-4: User is not an admin
    """
    if request.method == 'GET':
        return render_template("admin.signin.html")
    else:
        user_name = request.form['email']
        password = request.form['password']
        user = Users.query.filter(Users.user_name == user_name).first()

        if user is None:
            return render_template('admin.signin.html', flag=-2)
        if user.role != 'admin':
            return render_template('admin.signin.html', flag=-4)
        if check_password_hash(user.password, password):
            user_data = {
                "username": user_name,
                "user_id": user.user_id,
                "role": user.role,
                "loggedIn": 1
            }
            token = jwt.encode(user_data, app.config['SECRET_KEY'], algorithm='HS256')
            response = make_response(redirect("/admin/view"))
            response.set_cookie("token", token)
            return response        
        return render_template('admin.signin.html', flag=-3)


@app.route("/uploadsongs/<string:album_name>",methods=['POST','GET'])
def songs(album_name):
    """
    Handles song upload requests for a specific album.

    This function processes both GET and POST requests to the "/uploadsongs/<album_name>" route.
    It allows a logged-in creator to upload a song to a specific album.

    Args:
        album_name: The name of the album to which the song will be added.

    Returns:
        - Renders the "upload.html" template for GET requests.
        - Redirects to the "/creator" route with a success message if the song upload is successful.
        - Redirects to the "/uploadsongs/<album_name>" route if there's an error during upload.
    """
    if request.method == 'GET':
        cookie = check_cookie(request)
        username = cookie.get("username")
        return render_template('upload.html', username=username, upload='song', album_name=album_name)
    if request.method == 'POST':
        cookie = check_cookie(request)
        musicname = request.form['musicName']
        lyrics = request.form['Lyrics']
        genre = request.form['Genre']
        duration = request.form['Duration']
        music_blob = request.files['music']
        if music_blob:
            music_bytes_io = BytesIO(music_blob.read())
            data = base64.b64encode(music_bytes_io.getvalue()).decode('utf-8')
            album = Albums.query.filter(Albums.album_name==album_name).first()
            if album:
                song = Songs(song_id=gen_uuid(), song_name=musicname, album_id=album.album_id, duration=duration, genre=genre, music_blob = data,lyrics=lyrics)
                try:
                    db.session.add(song)
                    db.session.commit()
                    return render_template('redirect.html',href='/creator',data='Operation completed successfully;The song has been added to the album')
                except:
                    db.session.rollback()
        return redirect(f'/uploadsongs/{album_name}')

@app.route("/uploadalbum",methods=['POST','GET'])
def upload():
    """
    Handles album upload requests.

    This function processes both GET and POST requests to the "/uploadalbum" route.
    It allows a logged-in user to upload an album with an image and details.

    Returns:
        - Renders the "upload.html" template for GET requests.
        - Redirects to the "/creator" route with a success message if the album upload is successful.
        - Redirects to the "/uploadalbum" route if there's an error during upload.
    """
    if request.method == 'GET':
        cookie = check_cookie(request)
        username = cookie.get("username")
        return render_template('upload.html', username=username, upload='album')
    if request.method == 'POST':
        cookie = check_cookie(request)
        album_name = request.form['albumName']
        publisher = request.form['artist']
        image_blob = request.files['albumFile']
        if image_blob:
            image_bytes_io = BytesIO(image_blob.read())
            data = base64.b64encode(image_bytes_io.getvalue()).decode('utf-8')
            user = Users.query.filter(Users.user_name==cookie.get("username")).first()
            album1 = Albums(album_id=gen_uuid(), album_name=album_name, album_owner_id=user.user_id,artist=publisher,image_blob=data)
            try:
                db.session.add(album1)
                db.session.commit()
                return render_template('redirect.html',href='/creator',data='Operation completed successfully;The album has been added to the collection,Please add songs to your album')
            except:
                db.session.rollback()
                return redirect('/uploadalbum')
        return redirect('/uploadalbum')

@app.route("/creator")
def creator():
    """
    Renders the creator page for a logged-in user.

    This function handles GET requests to the "/creator" route.
    It retrieves user information from the JWT token in the cookie,
    checks if the user is a creator,
    and displays their albums and song details.

    Returns:
        - Renders the "creator.html" template with user data and album information.
        - Renders the "creator.html" template with a flag indicating:
            -registered = -1:user is not a creator  
            -registered = 0:user is creator but has no albums
            -registered = 1:user is creator and has albums
    """
    cookie = check_cookie(request)
    user_id = cookie.get("user_id")
    user = Users.query.filter(Users.user_id == user_id).first()
    if user is None:
        return redirect('/')
    if user.role == 'user':
        return render_template("creator.html",username=cookie.get("username"),registered = -1)
    albums = Albums.query.filter(Albums.album_owner_id == user.user_id).all()
    if len(albums) == 0:
        return render_template("creator.html", username=cookie['username'], registered=0)
    details = {
        'songcount': 0,
        'popular': "",
        'maxviews': 0,
        'totalviews': 0,
        'averagelikes': 0
    }
    temp_albums = {
        'count': len(albums),
        'albums': []
    }
    for album in albums:
        temp_dict = {
            'album_name': album.album_name,
            'songs': {
                'song': [],
                'count': 0
            }
        }
        songs = Songs.query.filter(Songs.album_id == album.album_id).all()
        temp_dict['songs']['count'] = len(songs)
        for song in songs:
            temp_dect_songs = {
                'lyrics': song.lyrics,
                'duration': song.duration,
                'id': song.song_id,
                'songname': song.song_name,
                'liked': song.liked,
                'views': song.song_views
            }
            if details["maxviews"] <= song.song_views:
                details['maxviews'] = song.song_views
                details['popular'] = song.song_name
            details['totalviews'] += song.song_views
            details['songcount'] += 1
            details['averagelikes'] += song.liked
            temp_dict['songs']['song'].append(temp_dect_songs)
        temp_albums['albums'].append(temp_dict)
    if details['songcount'] > 0:
        details['averagelikes'] /= details['songcount']
    return render_template("creator.html", username=cookie['username'], registered=1, details=details, albums=temp_albums)

@app.route("/change_role",methods=['POST'])
def change():
    """
    Changes the user's role to 'creator' and redirects to the creator page.

    This function handles POST requests to the "/change_role" route.
    It retrieves the user's information from the JWT token in the cookie,
    updates the user's role to 'creator' in the database,
    and redirects to the "/creator" route.

    Returns:
        A redirect response to the "/creator" route.
    """
    cookie = check_cookie(request)
    user_id = cookie.get("user_id") 
    user = Users.query.filter(Users.user_id == user_id).first()  
    if user:
        if user.role=='creator:':  
            return redirect("/creator") 
        user.role='creator'  
        db.session.commit()  
        return redirect("/creator")  
    return "User not found", 404

@app.route("/logout", methods=['GET'])
def logout():
    """
    Logs out the current user and redirects to the home page.

    This function handles GET requests to the "/logout" route.
    It clears the user's session by deleting the "token" cookie.

    Returns:
        A redirect response to the home page ("/").
    """
    response = make_response(redirect("/"))
    response.delete_cookie("token")
    return response

@app.route("/signin",methods=['GET','POST'])
def signin():
    """
    Handles user signin requests.

    This function processes both GET and POST requests to the "/signin" route.
    It handles user login, sets cookies, and generates a JWT token for authentication.

    Returns:
        - Renders the "signin.html" template if it's a GET request.
        - Redirects to the home page with a success flag and sets cookies if login is successful.
        - Renders the "signin.html" template with error flags if login fails:
            - flag=-2: User not found
            - flag=-3: Incorrect password
    """
    if request.method == 'GET':
        return render_template("signin.html")
    else:
        user_name = request.form['email']
        password = request.form['password']
        user = Users.query.filter(Users.user_name==user_name).first()

        if user is None:
            return render_template('signin.html',flag=-2)
        if check_password_hash(user.password,password):
            if user.role != 'admin':
                add_user_login(user.user_id)
                user_data = {
                    "username": user_name,
                    "user_id": user.user_id,
                    "role": user.role,
                    "loggedIn": 1
                }
                token = jwt.encode(user_data, app.config['SECRET_KEY'], algorithm='HS256')
                response = make_response(redirect("/"))
                response.set_cookie("token", token)
                return response
            return redirect("/admin/signin")
        return render_template('signin.html',flag=-3)

@app.route("/signup",methods=['POST'])
def signup():
    """
    Handles user signup requests.

    This function processes POST requests to the "/signup" route.
    It retrieves the username and password from the request form,
    checks if the username already exists in the database,
    and creates a new user record if the username is unique.

    Returns:
        - Renders the "signin.html" template with a flag indicating success or failure:
            - flag=1: Signup successful
            - flag=0: Username already exists
            - flag=-1: Database error during signup
    """
    if request.method == 'POST':
        user_name = request.form['email']
        password = request.form['password']
        user = Users.query.filter(Users.user_name==user_name).first()
        if user is None:
            with app.app_context():    
                try:
                    user1 = Users(user_id=gen_uuid(), user_name=user_name, role='user', password=generate_password_hash(password))
                    db.session.add(user1)
                    db.session.commit()
                    return render_template("signin.html",flag=1)
                except:
                    db.session.rollback()
                    return render_template("signin.html",flag = -1)
        else:
            return render_template("signin.html",flag=0)

@app.route("/",methods=['GET'])
@app.route("/index",methods=['GET'])
def index():
    """
    Renders the home page of the music streaming application.

    This function handles both the root route ("/") and the "/index" route.
    It retrieves various data from the database, including:

    - Top 4 most viewed songs
    - Top 4 most viewed albums (based on total song views)
    - 2 most recently released albums
    - 2 most recently released songs
    - Top 10 songs for each genre (ROCK, POP, ROMANCE, ELECTRO, HIP-HOP, SAD)
    - 6 most recently released albums (for the "New Releases" section)

    If the user is logged in, it also retrieves their playlists.

    The function then renders the "index.html" template with the retrieved data.
    If the user is not logged in, a JWT token is generated and set as a cookie.
    """
    cookie = check_cookie(request)
    songs = Songs.query.order_by(Songs.song_views.desc()).limit(4)
    albums = db.session.query(Albums).join(Songs,Albums.album_id == Songs.album_id).group_by(Albums.album_name).order_by(func.sum(Songs.song_views)).limit(4)
    release_a = Albums.query.order_by(Albums.album_date).limit(2)
    release_s = Songs.query.order_by(Songs.song_date).limit(2)
    top_genre1 = Songs.query.filter(Songs.genre == 'ROCK').order_by(Songs.song_views.desc()).limit(10)
    top_genre2 = Songs.query.filter(Songs.genre == 'POP').order_by(Songs.song_views.desc()).limit(10)
    top_genre3 = Songs.query.filter(Songs.genre == 'ROMANCE').order_by(Songs.song_views.desc()).limit(10)
    top_genre4 = Songs.query.filter(Songs.genre == 'ELECTRO').order_by(Songs.song_views.desc()).limit(10)
    top_genre5 = Songs.query.filter(Songs.genre == 'HIP-HOP').order_by(Songs.song_views.desc()).limit(10)
    top_genre6 = Songs.query.filter(Songs.genre == 'SAD').order_by(Songs.song_views.desc()).limit(10)   
    new_releases = Albums.query.order_by(Albums.album_date).limit(6)
    if not cookie["loggedIn"]:
        response = make_response(render_template("index.html", username=cookie['username'],
                               songs=songs,
                               albums=albums,
                               release_a=release_a,
                               release_s=release_s,
                               top_genre1=top_genre1,
                               top_genre2=top_genre2,
                               top_genre3=top_genre3,
                               top_genre4=top_genre4,
                               top_genre5=top_genre5,
                               top_genre6=top_genre6,
                               new_releases = new_releases
                               ))
        token = jwt.encode(cookie, app.config['SECRET_KEY'], algorithm='HS256')
        response.set_cookie("token",token)
        return response
    playlists = Playlists.query.filter(Playlists.playlist_owner_id == cookie['user_id']).all()
    return render_template("index.html", username=cookie['username'],
                            songs=songs,
                            albums=albums,
                            release_a=release_a,
                            release_s=release_s,
                            top_genre1=top_genre1,
                            top_genre2=top_genre2,
                            top_genre3=top_genre3,
                            top_genre4=top_genre4,
                            top_genre5=top_genre5,
                            top_genre6=top_genre6,
                            new_releases = new_releases,
                            playlists=playlists)
