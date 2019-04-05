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
    cursor = conn.cursor();
    query1 = "SELECT DISTINCT followerUsername,acceptedfollow FROM Follow WHERE followeeUsername = %s AND acceptedfollow = 0"
    cursor.execute(query1, (user))
    data = cursor.fetchall()
    cursor.close()
    return render_template('home.html',username = user,requests = data)



@app.route('/post', methods=['GET', 'POST'])
def post():
    username = session['username']
    cursor = conn.cursor();
    filepath = request.form["filepath"]
    allFollowers = request.form['allFollowers']
    caption = request.form["caption"]
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    error = None

    #if the photo is set to be private
    # Ask users to share
    if allFollowers == "0":
        query = 'SELECT groupName FROM CloseFriendGroup WHERE groupOwner = %s'
        cursor.execute(query, (username))
        conn.commit()
        data_group = cursor.fetchall()

        if data_group: #check if the user has at least one closefriend group so he can insert private photo
            #insert the photo
            query = 'INSERT INTO photo VALUES(Null, %s, %s, %s, %s, %s)'  # insert the photo into DB
            cursor.execute(query, (username, timestamp, filepath, caption, int(allFollowers)))
            conn.commit()
            #select the photo id just inserted into DB which is not shared
            query = 'SELECT DISTINCT photoID FROM Photo AS p WHERE p.allFollowers = %s AND p.photoID NOT IN (SELECT photoID from Photo NATURAL JOIN Share WHERE Photo.allFollowers = %s);'
            cursor.execute(query, (0, 0))
            data = cursor.fetchall()

            photoId = data[0]["photoID"]

            conn.commit()

            # task xiewy: need to add error here no closefriendgroup


            cursor.close()
            return render_template("sharewith.html", closeFriendsGroup = data_group, photoId = photoId)
        else:
            #if the user does not have any closefriend group
            #bring him to the post page
            #need at least one closefriend group
            # returns an error message to the html page
            session["username"] = username
            error = 'should have at least one close friends to post a private photo'
            # return redirect(url_for('home',error = error))
            return render_template("home.html", username = username, error = error)
    else:
        query = 'INSERT INTO photo VALUES(Null, %s, %s, %s, %s, %s)'  # insert the photo into DB
        cursor.execute(query, (username, timestamp, filepath, caption, int(allFollowers)))
        conn.commit()
        cursor.close()
    return redirect(url_for('home'))


@app.route("/share", methods = ["GET", "POST"])
def share():
    user_name = session["username"]
    photoId = request.form["photoId"]
    groupName = request.form.getlist("groupName")

    #Insert into database
    for elem in groupName:
        query = 'INSERT INTO Share VALUES (%s, %s, %s) '
        cursor = conn.cursor();
        cursor.execute(query, (elem, user_name, photoId))
        conn.commit()
    cursor.close()
    return redirect(url_for('home'))


#
@app.route('/show_photos', methods=["GET", "POST"])
def show_photos():
     user_name = session["username"]
     cursor = conn.cursor()
     query1 = "SELECT photoId, photoOwner, caption, filepath, timestamp FROM photo JOIN person ON photo.photoOwner = person.username WHERE isPrivate = 0 OR username = %s OR username IN (SELECT followeeUsername FROM follow WHERE followerUsername = %s and acceptedfollow = 1) AND allFollowers = 1 ORDER BY `photo`.`timestamp` DESC"
     cursor.execute(query1, (user_name, user_name))
     data1 = cursor.fetchall()
     for i in range(len(data1)):
         data1[i]["fname"] = ""
         data1[i]["lname"] = ""
     query2 = "SELECT photoId, fname, lname FROM person JOIN (SELECT username, photoId, photoOwner, caption, filepath, timestamp FROM photo NATURAL JOIN tag WHERE acceptedTag = 1) t2 ON person.username = t2.username"
     cursor.execute(query2)
     data2 = cursor.fetchall()
     for i in range(len(data1)):
         for j in range(len(data2)):
             if data1[i]["photoId"] == data2[j]["photoId"]:
                 if data1[i]["fname"] == "":
                     data1[i]["fname"] = data2[j]["fname"]
                     data1[i]["lname"] = data2[j]["lname"]
                 else:
                    data1[i]["fname"] += ", " + data2[j]["fname"]
                    data1[i]["lname"] += ", " + data2[j]["lname"]
     cursor.close()
     return render_template('show_photos.html', user_name=user_name, photos=data1)


@app.route('/manage_follows', methods=['GET', 'POST'])
def manage_follows():
    followername = session['username']
    followeename = request.form['followeename']
    cursor = conn.cursor();
    query = 'SELECT DISTINCT username FROM Person WHERE username = %s'
    cursor.execute(query, (followeename))
    data = cursor.fetchone()
    conn.commit()
    error = None
    if (data and followername != followeename):
        newQuery = "INSERT INTO Follow(followerUsername, followeeUsername, acceptedfollow) VALUES(%s,%s,%s)"
        cursor.execute(newQuery, (followername, followeename, 0))
        conn.commit()
        cursor.close()
        return redirect(url_for('home'))
    else:
        error = "invalid user to follow"
        return render_template('home.html', error=error)


@app.route('/manage_been_followed', methods=['GET', 'POST'])
def manage_been_followed():
    followeename = session['username']
    cursor = conn.cursor();
    query = "SELECT followerUsername FROM Follow WHERE followeeUsername = %s AND acceptedfollow = 0"
    cursor.execute(query, (followeename))
    followerlist = cursor.fetchall()
    conn.commit()

    for person in followerlist:

        curr_name = person['followerUsername']
        try:
            answer = request.form[curr_name]
            if (int(answer) == 0):

                query2 = "DELETE FROM Follow WHERE Follow.followerUsername = %s AND Follow.followeeUsername = %s"
                cursor.execute(query2, (curr_name, followeename))
                conn.commit()

            else:

                query3 = 'UPDATE Follow SET acceptedfollow = %s WHERE Follow.followerUsername = %s AND Follow.followeeUsername = %s'
                cursor.execute(query3, (1, curr_name, followeename))
                conn.commit()

                return redirect(url_for('home'))

        except:
            return redirect(url_for('home'))
    cursor.close()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run()
