import mysql.connector as mysql
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ezgi9898!'
app.config['MYSQL_DB'] = 'dbtify'

# Intialize MySQL
mysql = MySQL(app)
app.secret_key = "super secret key"


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = 'Please select your role'

    if request.method == 'POST' and 'role' in request.form:
        # Create variables for easy access
        user_answer = request.form['role']
        if user_answer == "listener":
            return redirect(url_for('login_listener'))

        else:
            return redirect(url_for('login_artist'))

    return render_template('welcome_page.html', msg=msg)


@app.route('/dbtify/loginlistener', methods=['GET', 'POST'])
def login_listener():
    # Output message if something goes wrong...
    msg = 'Welcome to DBtify'
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM listeners WHERE username = %s AND email = %s', (username, email,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account['username']
            session['permission'] = 0
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('home_listener'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect credentails!'
    return render_template('index_listener.html', msg=msg)


@app.route('/dbtify/loginartist', methods=['GET', 'POST'])
def login_artist():
    # Output message if something goes wrong...
    msg = 'Welcome to DBtify'
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'surname' in request.form:
        # Create variables for easy access
        name = request.form['name']
        surname = request.form['surname']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM artists WHERE name = %s AND surname = %s', (name, surname,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = account['id']
            session['permission'] = 1
            # Redirect to home page
            # return 'Logged in successfully!'
            cursor.close()
            return redirect(url_for('home_artist'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect credentials!'
    return render_template('index_artist.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('username', None)
    session.clear()
    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/homelistener')
def home_listener():
    # Check if user is loggedin
    if 'loggedin' in session:
        listener_id = session['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT songs.title,songs.no_of_likes FROM songs INNER JOIN user_likes ON user_likes.song_id= songs.id WHERE user_likes.user_id = %s;",
            (listener_id,))
        liked_songs = cursor.fetchall()
        cursor.close()
        return render_template('home_listener.html', username=session['username'], liked_songs=liked_songs)
    # User is not loggedin redirect to login page
    print("i am not logged in")
    return redirect(url_for('login'))


@app.route('/homeartist')
def home_artist():
    if 'loggedin' in session:
        artist_id = session['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT albums.title, albums.genre FROM albums INNER JOIN artists ON albums.artist_id= artists.id WHERE artists.id = %s;",
            (artist_id,))
        albums = cursor.fetchall()
        cursor.close()
        return render_template('home_artist.html', username=session['username'], albums=albums)
    return redirect(url_for('login'))


@app.route('/show_all_songs')
def show_all_songs():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT songs.id, songs.title, albums.title, albums.genre,albums.id FROM songs JOIN albums ON songs.album_id = albums.id ")
    data = cursor.fetchall()
    cursor.close()
    return render_template('all_songs.html', data=data)


@app.route('/show_all_listeners')
def show_all_listeners():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT username FROM listeners")
    data = cursor.fetchall()
    cursor.close()
    return render_template('all_listeners.html', data=data)


@app.route('/show_all_artist')
def show_all_artists():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT name, surname FROM artists")
    data = cursor.fetchall()
    cursor.close()
    return render_template('all_artists.html', data=data)


@app.route('/show_all_albums')
def show_all_albums():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT title, artist_id,id FROM albums")
    data = cursor.fetchall()
    cursor.close()
    return render_template('all_albums.html', data=data)


@app.route('/dbtify/search_album', methods=['GET', 'POST'])
def search_album():
    msg = "Please enter msg id"
    if request.method == 'POST' and 'album_id' in request.form:
        album_id = request.form['album_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM albums WHERE id = %s', (album_id,))
        # Fetch one record and return result
        album = cursor.fetchone()
        cursor.close()
        if album:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT songs.title, songs.no_of_likes FROM songs INNER JOIN albums ON songs.album_id = albums.id WHERE songs.album_id = %s;",
                (album_id,))
            data = cursor.fetchall()
            cursor.close()
            return render_template('listener_album_page.html', data=data, album=album['title'])
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect album id!'
    return render_template('listener_album_search.html', msg=msg)


@app.route('/dbtify/search_artist', methods=['GET', 'POST'])
def search_artist():
    msg = "Please enter msg id"
    if request.method == 'POST' and 'artist_id' in request.form:
        artist_id = request.form['artist_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM artists WHERE id = %s', (artist_id,))
        # Fetch one record and return result
        artist = cursor.fetchone()
        cursor.close()
        if artist:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT albums.title, albums.genre, albums.no_of_likes FROM albums INNER JOIN artists ON albums.artist_id= artists.id WHERE artists.id = %s;",
                (artist_id,))
            albums = cursor.fetchall()
            cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT songs.title,songs.no_of_likes, albums.title FROM songs JOIN albums ON albums.id = songs.album_id JOIN artists ON artists.id = albums.artist_id WHERE artist_id = %s;",
                (artist_id,))
            songs = cursor.fetchall()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT songs.title,albums.title, albums.artist_id FROM albums JOIN songs ON albums.id = songs.album_id JOIN coartists ON songs.id = coartists.song_id WHERE coartists.artist_id = %s;",(artist_id,))
            cosongs = cursor.fetchall()

            cursor.execute(
                "SELECT songs.title,songs.no_of_likes, albums.title  FROM songs JOIN albums ON albums.id = songs.album_id JOIN artists ON artists.id = albums.artist_id WHERE artist_id = %s  ORDER BY no_of_likes DESC LIMIT 10  ;",
                (artist_id,))
            popular_songs = cursor.fetchall()



            cursor.close()
            return render_template('listener_artist_page.html', albums=albums, songs=songs,
                                   artist=artist['name'] + " " + artist['surname'],cosongs=cosongs,popular_songs=popular_songs)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect album id!'
    return render_template('listener_artist_search.html', msg=msg)


@app.route('/dbtify/search_by_genre', methods=['GET', 'POST'])
def search_by_genre():
    msg = "Please enter msg id"
    if request.method == 'POST' and 'genre' in request.form:
        genre_to_search = request.form['genre']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT songs.title, songs.no_of_likes,albums.title FROM songs INNER JOIN albums ON albums.id = songs.album_id WHERE albums.genre = %s;",
            (genre_to_search,))
        data = cursor.fetchall()
        print(data)
        cursor.close()
        return render_template('listener_genre_page.html', data=data, genre=genre_to_search)

    return render_template('listener_genre_search.html', msg=msg)


@app.route('/dbtify/search_by_keyword', methods=['GET', 'POST'])
def search_by_keyword():
    msg = "Please enter msg id"
    if request.method == 'POST' and 'keyword' in request.form:
        keyword = request.form['keyword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        m_keyword = "%" + keyword + "%"
        cursor.execute("SELECT title, no_of_likes FROM songs WHERE title LIKE %s;", (m_keyword,))
        data = cursor.fetchall()
        cursor.close()
        return render_template('listener_keyword_page.html', data=data, keyword=keyword)

    return render_template('listener_keyword_search.html', msg=msg)


@app.route('/dbtify/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        if session['permission'] == 0:
            # We need all the account info for the user so we can display it on the profile page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM listeners WHERE username = %s', (session['username'],))
            account = cursor.fetchone()
            # Show the profile page with account info
            return render_template('profile.html', account=account)
        elif session['permission'] == 1:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM artists WHERE name = %s', (session['username'],))
            account = cursor.fetchone()
            return render_template('profile.html', account=account)

            # Show the profile page with accoun

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/dbtify/add_album', methods=['GET', 'POST'])
def add_album():
    if request.method == 'POST' and 'album_id' in request.form:
        album_id = request.form['album_id']
        album_title = request.form['album_title']
        genre = request.form['genre']
        artist_id = session['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "INSERT INTO albums (id, genre, title, artist_id) VALUES (%s, %s,%s, %s)"
        values = (album_id, genre, album_title, artist_id)
        cursor.execute(sql, values)
        mysql.connect.commit()
        mysql.connection.commit()
        return redirect(url_for('home_artist'))
    else:
        msg = 'Enter album details'
    return render_template('artist_add_album.html', msg=msg)


# TODO: what happens if that the first time you see the contr. add to artist?
@app.route('/dbtify/add_song', methods=['GET', 'POST'])
def add_song():
    if request.method == 'POST' and 'album_id' in request.form:
        album_id = request.form['album_id']
        song_title = request.form['song_title']
        song_id = request.form['song_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM albums WHERE id = %s', (album_id,))
        album = cursor.fetchone()
        if not album:
            msg = "Wrong album id"
        elif album['artist_id'] != session['username']:
            msg = 'This is not your album, you cant add songs to it'
        else:
            if request.form['contributor_name'] != '' :
                contributor_id = request.form['contributor_name'] + request.form['contributor_surname']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "INSERT INTO coartists (song_id,album_id, artist_id) VALUES (%s, %s,%s)"
                values = (song_id, album_id, contributor_id)
                cursor.execute(sql, values)
                mysql.connect.commit()
                mysql.connection.commit()
                cursor.close()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "INSERT INTO songs (id, title, album_id, no_of_likes) VALUES (%s, %s,%s, %s)"
            values = (song_id, song_title, album_id, 0)
            cursor.execute(sql, values)
            mysql.connect.commit()
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('home_artist'))
    else:
        msg = "Enter song details"

    return render_template('artist_add_song.html', msg=msg)


@app.route('/dbtify/modify_song', methods=['GET', 'POST'])
def modify_song():
    if request.method == 'POST' and 'song_id' in request.form:
        song_title = request.form['song_title']
        song_id = request.form['song_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM songs WHERE id = %s', (song_id,))
        song = cursor.fetchone()
        cursor.close()
        if song:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT artists.id FROM artists JOIN albums ON albums.artist_id = artists.id JOIN songs ON songs.album_id = albums.id WHERE songs.id = %s;",
                (song_id,))
            artist = cursor.fetchone()
            cursor.close()
            if artist['id'] != session['username']:
                msg = 'This is not your album, you cant modify songs in it'
                return render_template('artist_modify_song.html', msg=msg)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = "UPDATE songs SET title = %s WHERE id = %s"
            values = (song_title, song_id)
            cursor.execute(sql, values)
            # Fetch one record and return result
            mysql.connect.commit()
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('home_artist'))
        else:
            msg = 'Wrong credentials'
    else:
        msg = "Enter song details"

    return render_template('artist_modify_song.html', msg=msg)


@app.route('/dbtify/modify_album', methods=['GET', 'POST'])
def modify_album():
    if request.method == 'POST' and 'album_id' in request.form:
        album_id = request.form['album_id']
        album_title = request.form['album_title']
        genre = request.form['genre']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM albums WHERE id = %s', (album_id,))
        album = cursor.fetchone()
        if not album:
            msg = "No album exists with this id"
        elif album['artist_id'] != session['username']:
            msg = 'This is not your album, you cant change it'
        else:
            sql = "UPDATE albums SET title = %s, genre = %s  WHERE id = %s"
            values = (album_title, genre, album_id)
            cursor.execute(sql, values)
            mysql.connect.commit()
            mysql.connection.commit()
            return redirect(url_for('home_artist'))
    else:
        msg = "Please enter album details"
    return render_template('artist_modify_album.html', msg=msg)

@app.route('/dbtify/delete_song', methods=['GET','POST'])
def delete_song():
    if request.method == 'POST' and 'song_id' in request.form:
        song_id = request.form['song_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT no_of_likes, album_id FROM songs WHERE id = %s', (song_id,))
        song_data = cursor.fetchone()
        song_likes = song_data['no_of_likes']
        album_id = song_data['album_id']
        cursor.execute('SELECT artist_id FROM albums WHERE id = %s', (album_id,))
        artist_d = cursor.fetchone()
        artist_id = artist_d['artist_id']
        cursor.execute('SELECT total_likes FROM artists WHERE id = %s', (artist_id,))
        artist_d = cursor.fetchone()
        artist_likes = artist_d['total_likes']
        if not song_data:
            msg = "Wrong song id"
        elif artist_id!= session['username']:
            msg = 'This is not your song, you cant delete it'
        else:
            # reduce artist likes
            sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
            values = (artist_likes-song_likes, artist_id)
            cursor.execute(sql, values)
            mysql.connect.commit()
            mysql.connection.commit()
            #check coarts
            cursor.execute('SELECT artist_id FROM coartists WHERE song_id = %s', (song_id,))
            collab = cursor.fetchall()
            if collab:
                for c in collab:
                    cursor.execute('SELECT total_likes FROM artists WHERE id = %s', (c['artist_id'],))
                    ret = cursor.fetchone()
                    c_likes = ret['total_likes']
                    sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
                    values = (c_likes - song_likes, c['artist_id'])
                    cursor.execute(sql, values)
                    mysql.connect.commit()
                    mysql.connection.commit()


                cursor.execute('DELETE FROM coartists WHERE song_id = %s', (song_id,))
                mysql.connection.commit()
                mysql.connect.commit()

            cursor.execute('DELETE FROM songs WHERE id = %s', (song_id,))
            mysql.connect.commit()
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('home_artist'))
    else:
        msg = "Enter song details"

    return render_template('artist_delete_song.html', msg=msg)

def delete_album_helper(song_id,artist_id,album_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT no_of_likes FROM songs WHERE id = %s', (song_id,))
    song_data = cursor.fetchone()
    song_likes = song_data['no_of_likes']
    cursor.execute('SELECT total_likes FROM artists WHERE id = %s', (artist_id,))
    artist_d = cursor.fetchone()
    artist_likes = artist_d['total_likes']

    # reduce artist likes
    sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
    values = (artist_likes - song_likes, artist_id)
    cursor.execute(sql, values)
    mysql.connect.commit()
    mysql.connection.commit()

    # check coarts
    cursor.execute('SELECT * FROM coartists WHERE song_id = %s', (song_id,))
    collab = cursor.fetchall()
    if collab:
        for c in collab:
            cursor.execute('SELECT total_likes FROM artists WHERE id = %s', (c['artist_id'],))
            ret = cursor.fetchone()
            c_likes = ret['total_likes']
            sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
            values = (c_likes - song_likes, c['artist_id'])
            cursor.execute(sql, values)
            mysql.connect.commit()
            mysql.connection.commit()

        cursor.execute('DELETE FROM coartists WHERE song_id = %s', (song_id,))
        mysql.connection.commit()
        mysql.connect.commit()

    cursor.close()

@app.route('/dbtify/delete_album', methods=['GET','POST'])
def delete_album():
    if request.method == 'POST' and 'album_id' in request.form:
        album_id = request.form['album_id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT artist_id FROM albums WHERE id = %s', (album_id,))
        artist_d = cursor.fetchone()

        if not artist_d:
            msg = "Wrong song id"
        elif artist_d['artist_id']!= session['username']:
            msg = 'This is not your album, you cant delete it'
        else:
            cursor.execute('SELECT id FROM songs WHERE album_id = %s', (album_id,))
            songs = cursor.fetchall()
            for item in songs:
                delete_album_helper(item['id'],artist_d['artist_id'],album_id)

            cursor.execute('DELETE FROM albums WHERE id = %s', (album_id,))
            mysql.connection.commit()
            mysql.connect.commit()
            return redirect(url_for('home_artist'))
    else:
        msg = "Enter album details"

    return render_template('artist_delete_album.html', msg=msg)

@app.route('/like_song', methods=['GET', 'POST'])
def like_song():
    if request.method == 'POST':
        # Songun likeını artır
        song_id = request.form['likebtn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT no_of_likes FROM songs WHERE id= %s", (song_id,))
        old_likes = int(cursor.fetchone()['no_of_likes'])
        sql = "UPDATE songs SET no_of_likes = %s WHERE id = %s"
        values = (old_likes + 1, song_id)
        cursor.execute(sql, values)
        # Fetch one record and return result
        mysql.connect.commit()
        mysql.connection.commit()

        # artistin likeını artır
        cursor.execute(
            "SELECT artists.total_likes,artists.id FROM artists JOIN albums ON albums.artist_id = artists.id JOIN songs ON songs.album_id = albums.id  WHERE songs.id= %s",
            (song_id,))
        artist_details = (cursor.fetchone())
        old_likes = int(artist_details['total_likes'])
        sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
        values = (old_likes + 1, artist_details['id'])
        cursor.execute(sql, values)
        # Fetch one record and return result
        mysql.connect.commit()
        mysql.connection.commit()

        # contributorun likeı
        cursor.execute(
            "SELECT artists.total_likes,artists.id FROM artists JOIN coartists ON coartists.artist_id = artists.id  WHERE coartists.song_id= %s",
            (song_id,))
        artist_details = (cursor.fetchone())
        if artist_details:
            old_likes = int(artist_details['total_likes'])
            sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
            values = (old_likes + 1, artist_details['id'])
            cursor.execute(sql, values)
            # Fetch one record and return result
            mysql.connect.commit()
            mysql.connection.commit()

        sql = "INSERT INTO user_likes (song_id,user_id) VALUES (%s, %s)"
        values = (song_id, session['username'])
        cursor.execute(sql, values)
        # Fetch one record and return result
        mysql.connect.commit()
        mysql.connection.commit()
        cursor.close()

    return redirect(url_for('home_listener'))


@app.route('/others_likes', methods=['GET', 'POST'])
def others_likes():
    if request.method == 'POST':
        user_id = request.form['viewbtn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT songs.title,songs.no_of_likes FROM songs INNER JOIN user_likes ON user_likes.song_id= songs.id WHERE user_likes.user_id = %s;",
            (user_id,))
        liked_songs = cursor.fetchall()
        # Fetch one record and return result
        cursor.close()

    return render_template('other_listener_likes.html', other=user_id, liked_songs=liked_songs)

@app.route('/rank_artists', methods=['GET', 'POST'])
def rank_artists():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM artists ORDER BY total_likes DESC;")
    data = cursor.fetchall()
    return render_template('listener_popular_artists.html', data=data)

def like_album_helper(song_id,album_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT no_of_likes FROM songs WHERE id= %s", (song_id,))
    q = cursor.fetchone()
    print(q)
    old_likes = int(q['no_of_likes'])
    sql = "UPDATE songs SET no_of_likes = %s WHERE id = %s"
    values = (old_likes + 1, song_id)
    cursor.execute(sql, values)
    # Fetch one record and return result
    mysql.connect.commit()
    mysql.connection.commit()

    # artistin likeını artır
    cursor.execute("SELECT artists.total_likes,artists.id FROM artists JOIN albums ON albums.artist_id = artists.id WHERE albums.id= %s",(album_id,))
    artist_details = (cursor.fetchone())
    old_likes = int(artist_details['total_likes'])
    sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
    values = (old_likes + 1, artist_details['id'])
    cursor.execute(sql, values)
    # Fetch one record and return result
    mysql.connect.commit()
    mysql.connection.commit()

    # contributorun likeı
    cursor.execute("SELECT artists.total_likes,artists.id FROM artists JOIN coartists ON coartists.artist_id = artists.id  WHERE coartists.song_id= %s",(song_id,))
    artist_details = (cursor.fetchone())
    if artist_details:
        old_likes = int(artist_details['total_likes'])
        sql = "UPDATE artists SET total_likes = %s WHERE id = %s"
        values = (old_likes + 1, artist_details['id'])
        cursor.execute(sql, values)
        mysql.connect.commit()
        mysql.connection.commit()

    # TODO:BUNU TRIGGER YAPACAK
    sql = "INSERT INTO user_likes (song_id,user_id) VALUES (%s, %s)"
    values = (song_id, session['username'])
    cursor.execute(sql, values)
    # Fetch one record and return result
    mysql.connect.commit()
    mysql.connection.commit()
    cursor.close()

@app.route('/like_album', methods=['GET', 'POST'])
def like_album():
    if request.method == 'POST':
        # Albumun likeını artır
        album_id = request.form['likebtn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT no_of_likes FROM albums WHERE id= %s", (album_id,))
        old_likes = int(cursor.fetchone()['no_of_likes'])
        sql = "UPDATE albums SET no_of_likes = %s WHERE id = %s"
        mysql.connect.commit()
        mysql.connection.commit()
        values = (old_likes + 1, album_id)
        cursor.execute(sql, values)
        cursor.execute("SELECT id FROM songs WHERE album_id= %s", (album_id,))
        songs = cursor.fetchall()

        for s in songs:
            print(s['id'],album_id)
            like_album_helper(s['id'],album_id)
        cursor.close()

    return redirect(url_for('home_listener'))

@app.route('/show_collab', methods=['GET','POST'])
def show_collab():
    if request.method == 'POST' and 'artist_name' in request.form:
        artist_name = request.form['artist_name']
        artist_surname = request.form['artist_surname']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        result = cursor.callproc("getCollaborators", args=(artist_name,artist_surname))
        mresult = cursor.fetchall()
        data = []
        for item in mresult:
            cursor.execute('SELECT title FROM songs where id = %s',(item['song_id'],))
            d = cursor.fetchone()

            data.append((item['artist_id'],item['song_id'],d['title']))
        cursor.close()

        return render_template('listener_show_collab.html', data=data, name=artist_name + " "+ artist_surname,)

    return render_template('listener_search_collab.html')

