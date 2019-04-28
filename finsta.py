#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, send_file
import pymysql.cursors
import time
import os





#Initialize the app from Flask
app = Flask(__name__)
IMAGES_DIR = os.path.join(os.getcwd(), "images")
print(IMAGES_DIR)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='Project_test',
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
    # query1 = "SELECT DISTINCT followerUsername,acceptedfollow FROM Follow WHERE followeeUsername = %s AND acceptedfollow = 0"
    # cursor.execute(query1, (user))
    # data = cursor.fetchall()
    # cursor.close()
    return render_template('home.html', username=user)






@app.route("/share", methods = ["GET", "POST"])
def share():
    user_name = session["username"]
    photoId = request.form["photoId"]
    groupName = request.form.getlist("groupName")
    print(photoId)
    if groupName:
    #for each selected group
    #share the photo with this group
        for elem in groupName:
            query = 'INSERT INTO Share VALUES (%s, %s, %s) '
            cursor = conn.cursor();
            cursor.execute(query, (elem, user_name, photoId))
            conn.commit()
        cursor.close()
        return redirect(url_for('home'))
    else: #if there is nothing chosen, return to home page
        username = session["username"]
        error = "You did not select any of the closefriendgroup!!!!!!!!!!!!!"
        return render_template("home.html", username=username, error=error)





@app.route('/displayTags', methods = ['GET','POST'])
def display_tags():
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT photoID,acceptedTag,filePath FROM Tag NATURAL JOIN Photo WHERE acceptedTag = %s AND username = %s'
    cursor.execute(query, ('0', username))
    data = cursor.fetchall()
    conn.commit()
    return render_template('view_tags.html', tags=data)

@app.route('/acceptTagInfo', methods = ['GET','POST'])
def change_tags():
    message = 'You have successfully edited your tag requests'
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT photoID FROM Tag WHERE username = %s AND acceptedTag = %s'
    cursor.execute(query, (username, '0'))
    photoID_list = cursor.fetchall()
    conn.commit()
    for ID in photoID_list:
        curr_id = ID['photoID']
        requestID = request.form
        if curr_id == int(list(requestID.keys())[0]):
            answer = request.form[str(curr_id)]
            if int(answer) == 0:
                # 0 represents decline
                query1 = "DELETE FROM Tag WHERE Tag.username = %s AND Tag.photoID = %s"
                cursor.execute(query1, (username, curr_id))
                conn.commit()
            elif int(answer) == 1:
                # 1 represents accept
                query2 = "UPDATE Tag SET acceptedTag = %s WHERE Tag.username = %s AND Tag.photoID = %s"
                cursor.execute(query2, (1, username, curr_id))
                conn.commit()
            elif int(answer) == 2:
                # 2 represents ignore
                query2 = "UPDATE Tag SET acceptedTag = %s WHERE Tag.username = %s AND Tag.photoID = %s"
                cursor.execute(query2, (2, username, curr_id))
                # change 2, represents ignored tag
                conn.commit()
    return redirect(url_for('display_tags'))


@app.route('/to_follow', methods=['GET','POST'])
def to_follow():
    return render_template('to_follow.html')

@app.route('/upload_followrequests', methods = ['GET','POSTS'])
def upload_follows():
    username = session['username']
    cursor = conn.cursor();
    query = "SELECT DISTINCT followerUsername,acceptedfollow FROM Follow WHERE followeeUsername = %s AND acceptedfollow = 0"
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template('manage_follows.html', requests=data)


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
        return redirect(url_for('upload_follows'))
    else:
        error = "invalid user to follow"
        return render_template('home.html', error=error)


@app.route('/manage_been_followed', methods=['GET', 'POST'])
def manage_been_followed():
    followeename = session['username']
    cursor = conn.cursor()
    query = "SELECT followerUsername FROM Follow WHERE followeeUsername = %s AND acceptedfollow = 0"
    cursor.execute(query, (followeename))
    followerlist = cursor.fetchall()
    conn.commit()
    for person in followerlist:
        curr_name = person['followerUsername']
        curr_library = request.form
        if curr_name == list(curr_library.keys())[0]:
            answer = request.form[curr_name]
            # print (answer)
            if int(answer) == 0:
                query2 = "DELETE FROM Follow WHERE Follow.followerUsername = %s AND Follow.followeeUsername = %s"
                cursor.execute(query2, (curr_name, followeename))
                conn.commit()

            else:
                query3 = 'UPDATE Follow SET acceptedfollow = %s WHERE Follow.followerUsername = %s AND Follow.followeeUsername = %s'
                cursor.execute(query3, (1, curr_name, followeename))
                conn.commit()
    return redirect(url_for('upload_follows'))

@app.route("/show_like_photo", methods = ['GET','POST'])
def show_like_photo():
    username = session["username"]
    cursor = conn.cursor()
    query = "SELECT * FROM photo JOIN person ON photo.photoOwner = person.username WHERE photoID NOT IN (SELECT photoID FROM Liked WHERE username = %s) AND (isPrivate = 0 OR username = %s OR username IN (SELECT groupOwner FROM belong NATURAL JOIN closefriendgroup WHERE username = %s UNION SELECT followeeUsername FROM follow WHERE followerUsername = %s AND acceptedfollow = 1 AND allFollowers = 1))"
    cursor.execute(query, (username, username, username, username))
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template('like.html', ID_library = data)

@app.route("/like_photo", methods = ['GET','POST'])
def like_photo():
    username = session['username']
    cursor = conn.cursor()
    query = "SELECT photoID FROM photo JOIN person ON photo.photoOwner = person.username WHERE photoID NOT IN (SELECT photoID FROM Liked WHERE username = %s) AND (isPrivate = 0 OR username = %s OR username IN (SELECT groupOwner FROM belong NATURAL JOIN closefriendgroup WHERE username = %s UNION SELECT followeeUsername FROM follow WHERE followerUsername = %s AND acceptedfollow = 1 AND allFollowers = 1))"
    cursor.execute(query, (username, username, username, username))
    id = cursor.fetchall()
    conn.commit()
    print(id)
    photoID = request.form.getlist('id')
    for i in range(len(photoID)):
        curr_id = photoID[i]
        query1 = "INSERT INTO Liked (username, photoID) VALUES (%s, %s)"
        cursor.execute(query1, (username, int(curr_id)))
        conn.commit()
    cursor.close()
    return redirect(url_for('show_like_photo'))

@app.route("/show_followees", methods = ["GET","POST"])
def upload_followeelist():
    username = session["username"]
    cursor = conn.cursor()
    query = "SELECT followeeUsername FROM Follow WHERE followerUsername = %s"
    cursor.execute(query, username)
    data = cursor.fetchall()
    cursor.close()
    return render_template("followee_list.html", followee_list = data)

@app.route("/manage_unfollows", methods = ["GET","POST"])
def manage_unfollows():
    username = session["username"]
    unfollow_name = request.form["followee_name"]
    cursor = conn.cursor()
    query = "DELETE FROM Follow WHERE followerUsername = %s AND followeeUsername = %s"
    cursor.execute(query, (username, unfollow_name))
    conn.commit()
    query1 = "SELECT photoID FROM Photo WHERE photoOwner = %s"
    cursor.execute(query1, username)
    follower_photoID = cursor.fetchall()
    follower_photoID_list = []
    for elem in follower_photoID:
        follower_photoID_list.append(elem[list(elem.keys())[0]])
    print(follower_photoID_list)
    query2 = "SELECT PhotoID FROM Tag WHERE username = %s AND acceptedTag = 1"
    cursor.execute(query2, unfollow_name)
    tag_photoID = cursor.fetchall()
    tag_photoID_list = []
    for elem in tag_photoID:
        tag_photoID_list.append(elem[list(elem.keys())[0]])
    print(tag_photoID_list)
    todelete_photoID_list = []
    for id in tag_photoID_list:
        if id in follower_photoID_list:
            todelete_photoID_list.append(id)
    print(todelete_photoID_list)
    query3 = "DELETE FROM Tag WHERE username = %s AND photoID = %s"
    for id in todelete_photoID_list:
        cursor.execute(query3, (unfollow_name, id))
        conn.commit()
    cursor.close()
    message = "You've successfully unfollowed " + str(unfollow_name) + "and deleted the tags involving your photos"
    return render_template("manage_follows.html", message=message)


@app.route("/images", methods=["GET"])
def images():
    user_name = session["username"]
    cursor = conn.cursor()
    # query that find all information about photos that are visible to the user
    query1 = "SELECT * FROM photo JOIN person ON photo.photoOwner = person.username WHERE" \
             " isPrivate = 0 OR person.username = %s OR person.username IN (SELECT groupOwner FROM belong NATURAL JOIN" \
             " closefriendgroup WHERE username = %s UNION SELECT followeeUsername FROM follow WHERE" \
             " followerUsername = %s AND acceptedfollow = 1 AND allFollowers = 1) ORDER BY `photo`.`timestamp` DESC"
    cursor.execute(query1, (user_name, user_name, user_name))
    data1 = cursor.fetchall()
    # add three new key to the dictionary
    for i in range(len(data1)):
        data1[i]["fname"] = ""
        data1[i]["lname"] = ""
        data1[i]["comment"] = ""
    # query that find the tagged photoID and names that user can see
    query2 = "SELECT photoID, fname, lname FROM person JOIN (" \
             "SELECT username, photoID, photoOwner, caption, filepath, timestamp FROM photo NATURAL JOIN" \
             " tag WHERE acceptedTag = 1) t2 ON person.username = t2.username"
    cursor.execute(query2)
    data2 = cursor.fetchall()
    # query that find the photoID, username, and comment
    query3 = "SELECT photoID, username, commentText from comment"
    cursor.execute(query3)
    data3 = cursor.fetchall()

    # a nest loop to insert tagged name into the visible photo information
    for i in range(len(data1)):
        for j in range(len(data2)):
            # only insert into the dictionary if photoID matches
            if data1[i]["photoID"] == data2[j]["photoID"]:
                # if the key is empty
                if data1[i]["fname"] == "":
                    data1[i]["fname"] += data2[j]["fname"]
                    data1[i]["lname"] += data2[j]["lname"]
                else:
                    data1[i]["fname"] += ", " + data2[j]["fname"]
                    data1[i]["lname"] += ", " + data2[j]["lname"]
    # a nest loop to insert comment into the visible photo information
    for i in range(len(data1)):
        for j in range(len(data3)):
            # only insert into the dictionary if photoID matches
            if data1[i]["photoID"] == data3[j]["photoID"]:
                if data1[i]["comment"] == "":
                    data1[i]["comment"] = data3[j]["username"] + ": " +data3[j]["commentText"] + "\n"
                else:
                    data1[i]["comment"] += data3[j]["username"] + ": " +data3[j]["commentText"] + "\n"
    cursor.close()
    return render_template("images.html", poster_name=user_name, images=data1)

@app.route("/image/<image_name>", methods=["GET"])
def image(image_name):
    image_location = os.path.join(IMAGES_DIR, image_name)
    if os.path.isfile(image_location):
        return send_file(image_location, mimetype="image/jpg")

@app.route("/tagphoto", methods=["GET", "POST"])
def tagphoto():
    user_name = session["username"]
    cursor = conn.cursor()
    # query that find all information about photos that are visible to the user
    query = "SELECT photoID, filePath FROM photo JOIN person ON photo.photoOwner = person.username " \
            "WHERE isPrivate = 0 OR username = %s OR username IN (SELECT groupOwner FROM belong NATURAL JOIN" \
            " closefriendgroup WHERE username = %s UNION SELECT followeeUsername FROM follow WHERE" \
            " followerUsername = %s AND acceptedfollow = 1 AND allFollowers = 1) ORDER BY `photo`.`timestamp` DESC"
    cursor.execute(query, (user_name, user_name, user_name))
    data = cursor.fetchall()
    cursor.close()
    return render_template("tagphoto.html", poster_name = user_name, images = data)

@app.route("/taginsert", methods=["GET","POST"])
def tagrequest():
    user_name = session["username"]
    photo_id = request.form["image"]
    tag_name = request.form["name"]

    # check if the input photo id and username are valid
    photo_valid = False
    name_valid = False
    cursor = conn.cursor()
    cursor.execute("SELECT photoID FROM photo")
    photos = cursor.fetchall()
    for i in range(len(photos)):
        if int(photo_id) == photos[i]["photoID"]:
            photo_valid = True
    cursor.execute("SELECT username FROM person")
    people = cursor.fetchall()
    for i in range(len(people)):
        if tag_name == people[i]["username"]:
            name_valid = True

    id_lst = []
    # only insert if id and name are valid
    if photo_valid and name_valid:
        query = "SELECT username, photoID FROM tag WHERE photoID = %s"
        cursor.execute(query, (photo_id))
        names = cursor.fetchall()
        # query that find all information about photos that are visible to the user
        query = "SELECT photoID FROM photo JOIN person ON photo.photoOwner = person.username WHERE" \
                " isPrivate = 0 OR username = %s OR username IN (SELECT groupOwner FROM belong NATURAL JOIN " \
                "closefriendgroup WHERE username = %s UNION SELECT followeeUsername FROM follow WHERE" \
                " followerUsername = %s AND acceptedfollow = 1 AND allFollowers = 1) ORDER BY `photo`.`timestamp` DESC"
        cursor.execute(query, (tag_name, tag_name, tag_name))
        photo_visible = cursor.fetchall()
        for i in range(len(photo_visible)):
            id_lst.append(photo_visible[i]["photoID"])
        # if the photoID user want to tag is not visible to the user, then print an error
        if int(photo_id) not in id_lst:
            cursor.close()
            error = "the user you are tagging cannot view this photo!"
            return render_template('home.html', error=error)
        # if the tag table is empty
        if len(names) == 0:
            # if the user is tagging himself, then just insert into tag table with acceptTag = 1
            if user_name == tag_name:
                query = "INSERT INTO tag VALUES (%s, %s, '1');"
                cursor.execute(query, (user_name, photo_id))
                conn.commit()
                cursor.close()
                # print a message to tell user that he has tagged the person
                message = "you have tagged " + tag_name + " on the photo"
                return render_template('home.html', message=message)
            else:
                # if the user is tagging other people, then insert into tag table with acceptTag = 0
                query = "INSERT INTO tag VALUES (%s, %s, '0');"
                cursor.execute(query, (tag_name, photo_id))
                conn.commit()
                cursor.close()
                # print a message to tell user that he has tagged the person
                message = "you have tagged " + tag_name + " on the photo"
                return render_template('home.html', message=message)
        else:
            # if the tag table is not empty
            for i in range(len(names)):
                # if the name that user want to tag already been tagged on that photo
                if tag_name == names[i]["username"] and photo_id == names[i]["photoID"]:
                    cursor.close()
                    # print an error message to the user
                    error = "the user you are tagging has already been tagged in this photo!"
                    return render_template('home.html', error=error)
                else:
                    # if the user is tagging himself, then just insert into tag table with acceptTag = 1
                    if user_name == tag_name:
                        query = "INSERT INTO tag VALUES (%s, %s, '1');"
                        cursor.execute(query, (user_name, photo_id))
                        conn.commit()
                        cursor.close()
                        # print a message to tell user that he has tagged the person
                        message = "you have tagged " + tag_name + " on the photo"
                        return render_template('home.html', message=message)
                    else:
                        # if the user is tagging other people, then insert into tag table with acceptTag = 0
                        query = "INSERT INTO tag VALUES (%s, %s, '0');"
                        cursor.execute(query, (tag_name, photo_id))
                        conn.commit()
                        cursor.close()
                        # print a message to tell user that he has tagged the person
                        message = "you have tagged " + tag_name + " on the photo"
                        return render_template('home.html', message=message)
    elif name_valid == False:
        error = "the user you are tagging do not exist!"
        return render_template('home.html', error=error)
    elif photo_valid == False:
        error = "the photo you are tagging do not exist!"
        return render_template('home.html', error=error)
    cursor.close()
    return redirect(url_for('home'))

@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")

@app.route("/searchtag", methods=["GET","POST"])
def searchtag():
    user_name = session["username"]
    tag_name = request.form["name"]
    # check if the name that user want to search is valid or not
    name_valid = False
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM person")
    people = cursor.fetchall()
    for i in range(len(people)):
        if tag_name == people[i]["username"]:
            name_valid = True

    id_lst = []
    search_result = []
    if name_valid:
        # find all the photoID that has been tagged with the name that user is searching
        # and the person accept the tag
        query = "SELECT photoID FROM tag WHERE username = %s AND acceptedTag = 1"
        cursor.execute(query, (tag_name))
        photo_tagged = cursor.fetchall()
        for i in range(len(photo_tagged)):
                id_lst.append(photo_tagged[i]["photoID"])
        # query that find all information about photos that are visible to the user
        query = "SELECT * FROM photo JOIN person ON photo.photoOwner = person.username WHERE" \
                " isPrivate = 0 OR username = %s OR username IN (SELECT groupOwner FROM belong NATURAL JOIN " \
                "closefriendgroup WHERE username = %s UNION SELECT followeeUsername FROM follow WHERE" \
                " followerUsername = %s AND acceptedfollow = 1 AND allFollowers = 1) ORDER BY `photo`.`timestamp` DESC"
        cursor.execute(query, (user_name, user_name, user_name))
        photo_visible = cursor.fetchall()
        # if the photoID user can see matches the photoID that has tagged the name that user is searching,
        # then append in the list
        for i in range(len(photo_visible)):
            if photo_visible[i]["photoID"] in id_lst:
                search_result.append(photo_visible[i])
        cursor.close()
        # if the result list is not empty, then print out photos
        if len(search_result) != 0:
            message = "Here are photos that have " + tag_name + " tagged on it."
            return render_template("searchtag.html", message=message, images=search_result)
        # if the result list is empty, then print out a message to the user
        else:
            message = "There is no photo you can view that have " + tag_name + " tagged on it."
            return render_template('home.html', message=message)
    elif name_valid == False:
        error = "the user you are searching do not exist!"
        return render_template('home.html', error=error)

@app.route("/searchposter", methods=["GET","POST"])
def searchposter():
    user_name = session["username"]
    poster_name = request.form["name"]

    name_valid = False
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM person")
    people = cursor.fetchall()
    for i in range(len(people)):
        if poster_name == people[i]["username"]:
            name_valid = True

    id_lst = []
    search_result = []
    if name_valid:
        # find all the photoID that been post by the name that user is searching
        query = "SELECT photoID FROM photo WHERE PhotoOwner= %s"
        cursor.execute(query, (poster_name))
        photo_post = cursor.fetchall()
        for i in range(len(photo_post)):
                id_lst.append(photo_post[i]["photoID"])
        # query that find all information about photos that are visible to the user
        query = "SELECT * FROM photo JOIN person ON photo.photoOwner = person.username WHERE" \
                " isPrivate = 0 OR username = %s OR username IN (SELECT groupOwner FROM belong NATURAL JOIN " \
                "closefriendgroup WHERE username = %s UNION SELECT followeeUsername FROM follow WHERE" \
                " followerUsername = %s AND acceptedfollow = 1 AND allFollowers = 1) ORDER BY `photo`.`timestamp` DESC"
        cursor.execute(query, (user_name, user_name, user_name))
        photo_visible = cursor.fetchall()
        # if the photoID user can see matches the photoID that are post by the name that user is searching,
        # then append in the list
        for i in range(len(photo_visible)):
            if photo_visible[i]["photoID"] in id_lst:
                search_result.append(photo_visible[i])
        cursor.close()
        # if the result list is not empty, then print out photos
        if len(search_result) != 0:
            message = "Here are photos that posted by " + poster_name + " :"
            return render_template("searchposter.html", message=message, images=search_result)
        # if the result list is empty, then print out a message to the user
        else:
            message = "There is no photo you can view that posted by " + poster_name + " ."
            return render_template('home.html', message=message)
    elif name_valid == False:
        error = "the user you are searching do not exist!"
        return render_template('home.html', error=error)

#to display all the close friend group to choose
@app.route("/closeFriendGroups", methods=["GET"])
def closeFriendGroups():
    username = session["username"]
    query = "SELECT groupName FROM CloseFriendGroup WHERE CloseFriendGroup.groupOwner = %s"
    cursor = conn.cursor()
    cursor.execute(query,(username))
    conn.commit()
    data = cursor.fetchall()
    print(data)
    cursor.close()
    return render_template("closefriendgroups.html", poster_name=username, closefriendgroups=data)






#show all the followers that can be added into the close friend group
@app.route("/showfollowerstoadd", methods=["GET","POST"])
def addfriendtogroup():
    username = session["username"]
    groupName = request.form["groupName"]
    query = "SELECT followeRUsername FROM Follow WHERE followeeUsername = %s AND acceptedfollow = %s"
    cursor = conn.cursor()
    cursor.execute(query, (username, 1))
    conn.commit()
    data = cursor.fetchall()
    print(data)
    cursor.close()
    return render_template("followerstoadd.html", username=username, followers = data, groupName = groupName)

#add the chosen followers into the group.
#if already in the group, return to home with error
@app.route("/addtogroup", methods=["GET","POST"])
def addtogroup():
    username = session["username"]
    groupName = request.form["groupName"]
    followers = request.form.getlist("followers")
    print(followers)
    print(groupName)
    error = "you did not select any one!!!!!"
    if followers:
        for follower in followers:
            #for each follower, see if he/she is in the closefriendgroup or not
            query_test = "SELECT username FROM Belong WHERE groupName = %s AND username = %s"
            cursor = conn.cursor()
            cursor.execute(query_test, (groupName, follower))
            data = cursor.fetchall()
            conn.commit()
            if data:
                #if data exists, the follower is already in the group
                session["username"] = username
                error = "The follower you selected is already in this close friend!!!!!!"
                return render_template('home.html', error=error)
            else:
                #no data, insert the follower into the selected group
                query_add = "INSERT INTO Belong VALUES (%s, %s, %s)"
                cursor = conn.cursor()
                cursor.execute(query_add, (groupName, username, follower))
                conn.commit()
                cursor.close()
                message = "Successfullly added"
                return render_template('home.html', message=message)
    return render_template('home.html', error=error)



@app.route("/newgroup", methods=["GET","POST"])
def newGroup():
    username = session["username"]
    return render_template("newgroup.html", username = username)

@app.route("/addnewgroup", methods=["GET","POST"])
def addnewgroup():
    message = "Successfully add the close friend group"
    username = session["username"]
    groupName = request.form["groupName"]
    cursor = conn.cursor()
    query_sel = "SELECT * FROM CloseFriendGroup WHERE groupName = %s AND groupOwner = %s"
    cursor.execute(query_sel, (groupName, username))
    data = cursor.fetchall()
    if data:
        #test whether the close friend group already exists
        error = "The close friend group already exists!!!!!"
        session["username"] = username
        cursor.close()
        return render_template('home.html', error = error, username = username)
    else:
        #if not exists we should insert the new group into the database
        query = "INSERT INTO CloseFriendGroup VALUES(%s, %s)"
        cursor.execute(query, (groupName, username))
        session["username"] = username
        conn.commit()
        cursor.close()
    return render_template('home.html', message = message, username = username)



@app.route("/friendrec", methods=["GET","POST"])
def friendrec():
    username = session["username"]
    #select all friends of the current user
    query_friend = "SELECT followeeUsername FROM follow WHERE followerUsername = %s"
    cursor = conn.cursor()
    cursor.execute(query_friend, (username))
    data = cursor.fetchall()
    data2 = []
    for elem in data:
        #select people followed by the friends of the current user
        query = "SELECT followeeUsername FROM follow WHERE followerUsername = %s"
        cursor = conn.cursor()
        cursor.execute(query, (elem["followeeUsername"]))
        data3 = cursor.fetchall()
        for elem1 in data3:
            #if the user is not the friend of the user, and get rid of redundancy
            if (elem1 not in data2) and (elem1 not in data) and (elem1["followeeUsername"] != username):
                data2.append(elem1)
    conn.commit()
    cursor.close()
    return render_template('friendrec.html', data2=data2, username = username)

#send follow request to recommanded people
@app.route("/followrecfriends", methods=["GET","POST"])
def followrecfriends():
    username = session["username"]
    followers = request.form.getlist("friends")
    print(followers)

    if followers:
        for follower in followers:
            query_test = "INSERT INTO follow VALUES (%s, %s, NULL)"
            cursor = conn.cursor()
            cursor.execute(query_test, (username, follower))
            conn.commit()
            message = "sucessfully followed"
            cursor.close()
            return render_template('home.html', message=message)
    else:
        error = "you did not select any one"
        session["username"] = username
        return render_template('home.html', error = error)





@app.route("/addcommentpage", methods=["GET","POST"])
def addcommentpage():
    photoid = request.form["photoID"]
    #keep track of the information of the photo to display it
    query = "SELECT filePath FROM photo WHERE photoID = %s"
    cursor = conn.cursor()
    cursor.execute(query, (photoid))
    data = cursor.fetchall()
    conn.commit()
    filepath = data[0]["filePath"]
    cursor.close()
    return render_template('addcommentpage.html', photoId = photoid,filePath = filepath)

#get all the information from html and then insert the comment to the database
@app.route("/addcomment", methods=["GET","POST"])
def addcomment():
    username = session["username"]
    photoId = request.form["photoId"]
    comment = request.form["comment"]
    cursor = conn.cursor()
    query = "INSERT INTO comment VALUES(%s, %s, %s, %s)"

    cursor.execute(query, (username, photoId, comment, time.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    cursor.close()
    session['username'] = username
    message = "successfully add the comment!!!!"
    cursor.close()
    return render_template('home.html', message=message)







@app.route("/upload", methods=["GET"])
def upload():
    return render_template("upload.html")


@app.route("/uploadImage", methods=["POST"])
def upload_image():
    if request.files:
        image_file = request.files.get("imageToUpload", "")
        caption = request.form["caption"]
        username = session["username"]
        allFollowers = request.form["allFollowers"]
        cursor = conn.cursor();
        print(username)
        print("caption")
        print(caption)
        print(allFollowers)

        if allFollowers == "0":
            query = 'SELECT groupName FROM CloseFriendGroup WHERE groupOwner = %s'
            cursor.execute(query, (username))
            conn.commit()
            data_group = cursor.fetchall()

            if data_group:  # check if the user has at least one closefriend group so he can insert private photo
                # insert the photo
                print("enter data_group")
                image_name = image_file.filename
                filepath = os.path.join(IMAGES_DIR, image_name)

                image_file.save(filepath)

                cursor = conn.cursor()
                query = "INSERT INTO photo VALUES(Null, %s, %s, %s, %s, %s)"

                cursor.execute(query, (username, time.strftime('%Y-%m-%d %H:%M:%S'), image_name, caption, int(allFollowers)))

                conn.commit()

                # select the photo id just inserted into DB which is not shared
                query = 'SELECT DISTINCT photoID FROM Photo AS p WHERE p.allFollowers = %s AND p.photoID NOT IN (SELECT photoID from Photo NATURAL JOIN Share WHERE Photo.allFollowers = %s);'
                cursor.execute(query, (0, 0))
                data = cursor.fetchall()

                photoId = data[0]["photoID"]
                print("photo id")
                print(photoId)

                conn.commit()

                # task xiewy: need to add error here no closefriendgroup

                cursor.close()
                return render_template("sharewith.html", closeFriendsGroup=data_group, photoId=photoId)

            else:
                # if the user does not have any closefriend group
                # bring him to the post page
                # need at least one closefriend group
                # returns an error message to the html page
                session["username"] = username
                error = 'should have at least one close friends to post a private photo'
                # return redirect(url_for('home',error = error))
                return render_template("home.html", username=username, error=error)
        else:
            image_name = image_file.filename
            filepath = os.path.join(IMAGES_DIR, image_name)

            image_file.save(filepath)

            cursor = conn.cursor();
            query = "INSERT INTO photo VALUES(Null, %s, %s, %s, %s, %s)"

            cursor.execute(query, (username, time.strftime('%Y-%m-%d %H:%M:%S'), image_name, caption, int(allFollowers)))
            conn.commit()
            cursor.close()

    return redirect(url_for('home'))
    #
    #
    #
    #
    #     image_name = image_file.filename
    #     filepath = os.path.join(IMAGES_DIR, image_name)
    #     image_file.save(filepath)
    #     cursor = conn.cursor();
    #     query = "INSERT INTO photo (timestamp, filePath, caption, username) VALUES (%s, %s, %s, %s)"
    #     cursor.execute(query, (time.strftime('%Y-%m-%d %H:%M:%S'), image_name, caption))
    #     conn.commit()
    #
    #     message = "Image has been successfully uploaded."
    #     return render_template("upload.html", message=message)
    # else:
    #     message = "Failed to upload image."
    #     return render_template("upload.html", message=message)

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



# SELECT Liked.photoID, COUNT(Liked.photoID) AS likes FROM Photo LEFT JOIN Liked USING(photoID) JOIN Person ON photo.photoOwner = person.username WHERE
# isPrivate = 0 OR Liked.username = 'zy123' OR Liked.username IN (SELECT groupOwner FROM belong NATURAL JOIN
# closefriendgroup WHERE username = 'zy123' UNION SELECT followeeUsername FROM follow WHERE
# followerUsername = 'zy123' AND acceptedfollow = 1 AND allFollowers = 1) GROUP BY photoID