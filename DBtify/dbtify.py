import mysql.connector as mysql
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ezgi9898!'
app.config['MYSQL_DB'] = 'dbtify'

# Intialize MySQL
mysql = MySQL(app)
app.secret_key = "super secret key"


@app.route('/dbtify/login', methods=['GET', 'POST'])
def login():
    msg = 'Please select your role'
    if request.method == 'POST' and 'submit' in request.form:
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
            session['username'] = account['name']
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
        # User is loggedin show them the home page
        return render_template('home_listener.html', username=session['username'])
    # User is not loggedin redirect to login page
    print("i am not logged in")
    return redirect(url_for('login'))


@app.route('/homeartist')
def home_artist():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        # return render_template('home.html', username=session['username'])
        return render_template('home_artist.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/show_all_songs')
def show_all_songs():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT title, album_id FROM songs")
    data = cursor.fetchall()
    cursor.close()
    return render_template('all_songs.html', data=data)


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
    cursor.execute("SELECT title, artist_id FROM albums")
    data = cursor.fetchall()
    cursor.close()
    return render_template('all_albums.html', data=data)

'''
@app.route('/show_all_songs_in_album')
def show_all_songs_in_album(album_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT songs.title, songs.no_of_likes FROM songs INNER JOIN albums ON songs.album_id = albums.id;")

    data = cursor.fetchall()
    cursor.close()
    print(data)
    return render_template('listener_album_page.html', data=data, album=album_id)
   


def show_liked_songs(listener_id)
def show_by_genre(genre)
def show_by_keyword()
def show_popular_artists()

def show_artist_songs()
def show_artist_albums()
def show_artist_tops()
def show
def create_album()
'''


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
            cursor.execute("SELECT songs.title, songs.no_of_likes FROM songs INNER JOIN albums ON songs.album_id = albums.id WHERE songs.album_id = %s;",(album_id,))
            data = cursor.fetchall()
            cursor.close()
            return render_template('listener_album_page.html', data=data, album=album)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect album id!'
    return render_template('listener_album_search.html', msg=msg)

@app.route('/dbtify/search_by_genre', methods=['GET', 'POST'])
def search_by_genre():
    msg = "Please enter msg id"
    if request.method == 'POST' and 'genre' in request.form:
        genre_to_search = request.form['genre']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM genres WHERE name = %s', (genre_to_search,))
        # Fetch one record and return result
        genre = cursor.fetchone()
        cursor.close()
        if genre:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT songs.title, songs.no_of_likes FROM songs INNER JOIN albums ON albums.id = songs.album_id WHERE albums.genre = %s;",(genre_to_search,))
            data = cursor.fetchall()
            print(data)
            cursor.close()
            return render_template('listener_genre_page.html', data=data, genre=genre_to_search)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect album genre!'
    return render_template('listener_genre_search.html', msg=msg)

@app.route('/dbtify/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        if session['permission'] == 0:
            # We need all the account info for the user so we can display it on the profile page
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM listener WHERE username = %s', (session['username'],))
            account = cursor.fetchone()
            # Show the profile page with account info
            return render_template('profile.html', account=account)
        elif session['permission'] == 1:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM artist WHERE name = %s', (session['username'],))
            account = cursor.fetchone()
            return render_template('profile.html', account=account)

            # Show the profile page with accoun

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


'''
db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "Ezgi9898!"
)
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cnx.close()

## creating an instance of 'cursor' class which is used to execute the 'SQL' statements in 'Python'
cursor = db.cursor()

## creating a databse called 'datacamp'
## 'execute()' method is used to compile a 'SQL' statement
## below statement is used to create tha 'datacamp' database
#cursor.execute("CREATE DATABASE dbtify")
## executing the statement using 'execute()' method
cursor.execute("SHOW DATABASES")

## 'fetchall()' method fetches all the rows from the last executed statement
databases = cursor.fetchall() ## it returns a list of all databases present

## printing the list of databases
print(databases)
db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "Ezgi9898!",
    database = "datacamp"
)
cursor = db.cursor()
#cursor.execute("CREATE TABLE useri (name VARCHAR(255), user_name VARCHAR(255))")
cursor.execute("SHOW TABLES")

tables = cursor.fetchall()
print(tables)
'''
