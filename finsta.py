#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import time






#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='Project_real',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    fname = request.form["first name"]
    lname = request.form["last name"]
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO person VALUES(%s, %s, %s, %s, Null, Null, NULL)'
        cursor.execute(ins, (username, password, fname, lname))
        conn.commit()
        cursor.close()
        return render_template('index.html')


@app.route('/home')
def home():
    user = session['username']
    # cursor = conn.cursor();
    # query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    # cursor.execute(query, (user))
    # data = cursor.fetchall()
    # cursor.close()
    return render_template('home.html', username=user)


@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor();
    filepath = request.form["filepath"]
    allFollowers = request.form['allFollowers']
    # for elem in request.form:
    #     print("kaka")
    # isPrivate = int(isPrivate)
    # if isPrivate == 0:
    #     print("is equal to 0")
    # print(type(allFollowers))
    caption = request.form["caption"]
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    query = 'INSERT INTO photo VALUES(Null, %s, %s, %s, %s, %s)'
    cursor.execute(query, (username, timestamp, filepath, caption, int(allFollowers)))
    conn.commit()

    if allFollowers == "0":
        query = 'SELECT DISTINCT photoID FROM Photo AS p WHERE p.allFollowers = %s AND p.photoID NOT IN (SELECT photoID from Photo NATURAL JOIN Share WHERE Photo.allFollowers = %s);'
        cursor.execute(query, (0, 0))
        data = cursor.fetchall()
        print(data)
        photoId = data[0]["photoID"]
        # print(photoId)
        conn.commit()
        query = 'SELECT groupName FROM CloseFriendGroup WHERE groupOwner = %s'
        cursor.execute(query, (username))
        data = cursor.fetchall()
        print(data)
        print(data[0]["groupName"])
        print("abc")
        conn.commit()
        cursor.close()
        return render_template("sharewith.html", closeFriendsGroup = data, photoId = photoId)
    cursor.close()
    return redirect(url_for('home'))


@app.route("/share", methods = ["GET", "POST"])
def share():
    user_name = session["username"]
    photoId = request.form["photoId"]
    groupName = request.form["groupName"]
    print(photoId)
    print(groupName)
    print(user_name)
    query = 'INSERT INTO Share VALUES (%s, %s, %s) '
    cursor = conn.cursor();
    cursor.execute(query, (groupName, user_name, photoId))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))


# @app.route('/select_blogger')
# def select_blogger():
#     #check that user is logged in
#     #username = session['username']
#     #should throw exception if username not found
#
#     cursor = conn.cursor();
#     query = 'SELECT DISTINCT username FROM blog'
#     cursor.execute(query)
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('select_blogger.html', user_list=data)
#
# @app.route('/show_posts', methods=["GET", "POST"])
# def show_posts():
#     poster = request.args['poster']
#     cursor = conn.cursor();
#     query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
#     cursor.execute(query, poster)
#     data = cursor.fetchall()
#     cursor.close()
#     return render_template('show_posts.html', poster_name=poster, posts=data)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
# if __name__ == "__main__":
#     app.run('127.0.0.1', 5000, debug = True)

if __name__ == "__main__":
    app.run()
