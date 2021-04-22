from app import app ##for initiating the app
from app.forms import * ## to get all the forms and validators in them
from app.models import * ## all the tables present in database 
from flask import render_template, url_for, redirect,request, jsonify ## components of flask to connect to frontend
from flask_login import LoginManager, login_user, current_user, login_required, logout_user ## modules for logging in a user
from sqlalchemy import create_engine ## connecting to database
from flask_mail import Mail, Message  ## to send mails in forgot password
from app.email import * ## to send mails in forgot password
from itsdangerous import URLSafeTimedSerializer 
from werkzeug.security import generate_password_hash,check_password_hash ## to hash password and validating entered password with the hash of password
import base64 ## encode and decode images

# creating engine
engine = create_engine('postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk')
# connecting to database
connection = engine.raw_connection()
# creating a cursor
mycursor = connection.cursor()
# configuring database
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) ## instance of database
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# session = db.session()
# cursor = session.execute(sql).cursor


login = LoginManager(app)
login.init_app(app)

# configuring the mail details from which mail is to be sent
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'developmentsoftware305@gmail.com'
app.config['MAIL_PASSWORD'] = 'tempmail1@'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

#function for loading the user if logged in
@login.user_loader
def load_user(id):
    return Credentials.query.get(int(id))

#home route
@app.route('/', methods=['GET', 'POST'])
    
#login and register route
@app.route('/login', methods = ['GET','POST'])
def login():
    login_form = LoginForm() # loading login form
    reg_form = RegistrationForm()#loading register form
    print(request.method)
    if request.method == 'POST': # if form submitted
        if request.form["action"] == "Login": # if login form submitted
            if login_form.validate_on_submit():  # if conditions specified in forms.py are satisfied
                user_object = Credentials.query.filter_by(mail_id = login_form.mail_id.data).first() # get details from Credentials table
                login_user(user_object) #login the particular user

                return redirect(url_for('home')) # redirect to home page after successful login
        elif request.form["action"] == "Register": # if registration form submitted
            if reg_form.validate_on_submit(): # if conditions specified in forms.py are satisfied
                mail_id = reg_form.mail_id.data # get details from the form submitted
                password = reg_form.password.data
                cred = Credentials(mail_id=mail_id, password=generate_password_hash(password)) # create object for Credentials ## password is hashed here
                prof = newprofile(mail_id=mail_id, full_name=reg_form.full_name.data, year=reg_form.year.data,
                               department=reg_form.department.data, degree=reg_form.degree.data) # create object for Profile
                db.session.add(cred) # add the details to the Credentials table in database 
                db.session.add(prof) # add the profile details to the Profile table in database
                db.session.commit()
                return redirect(url_for('login')) # redirect to login after successful registration
    return render_template("login.html", form1 = login_form, form = reg_form) # if the method is post then return the login form

#reset password route, to retreive the mail id and send mail to the same
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
#if the user is logged in, then there is no need of reset password functionality,so redirected to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))

#form to retreive the email_id, falls under reset_password_request.html
    form = ResetPasswordRequestForm()
        #if form details are valid
    if form.validate_on_submit():
        user = Credentials.query.filter_by(mail_id=form.email.data).first()  #check if the given id is registered in db or not
        if user:
            print("user found")
            send_password_reset_email(user) #if user is found, invoke send_password function defined in models corr to the user mail
        #flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))   #redirect to login page
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

#when the user clicks on the password reset link , a second route associated with password reset is triggered
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #retreiving the user by invoking verify_reset_token_method
    idRec = Credentials.verify_reset_password_token(token)
    print("heyyyyyyappplication""", idRec)
    # if not user:
    #     return redirect(url_for('login'))
    
    #if token is valid the user is presented with aform to reset password    
    form = ResetPasswordForm()
        # if form details are valid
    if form.validate_on_submit():
        user = Credentials.query.filter_by(mail_id=idRec).first()  #fetch the user from database for updation
        print("heyy after reset password", user.id)
        print("heyy before reset password", user.password)##for personal convenience
        user.password=generate_password_hash(form.password.data) ## generate password hash ##reseting the users password to one retreived from form
        
        #update query
        mycursor.execute("UPDATE credentials SET password = '{password}' WHERE mail_id = '{mail}' ".format(password = str(user.password), mail =  str(idRec)))
        connection.commit()
        print("heyy after reset password in database", user.password)
        #flash('Your password has been reset.')
        return redirect(url_for('login'))   #finally redirect to login page
    return render_template('reset_password.html', form=form)     #rendering corresponding template with password reset form

#after successful login it is redirected to home route
@app.route('/home',methods=["POST","GET"])
def home():
    mycursor.execute("select id,tag from eventags order by count desc") # fetching the event tags data order b count in descending order
    trending = mycursor.fetchall()
    trending = [x[1] for x in trending[:4]]           # made a list of tags 
    trending = trending[:4]                           #gives top 4 trending tags
    hform = HomeForm()                                # form for searching tags
    value = [(x[0], x[1]) for x in trending]          #list of tuples with id,tag 
    value = sorted(value)                             #sorted according to id's
    hform.tag_search.choices = value                  #this list is passed to HomeForm tag search for choices 
    return render_template('home.html', form=hform,trending=trending)


@app.route('/homeSearch',methods=["POST","GET"])
def homeSearch():
    if request.method == "GET":
        mycursor.execute(
            "select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id from post as po , newprofile as p where p.mail_id=po.mail_id order by date")
        data1 = mycursor.fetchall()
        mycursor.execute(
            "select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id from postss as po , newprofile as p where p.mail_id=po.mail_id order by date")
        data = mycursor.fetchall()
        data = [list(x) for x in data]
        imgs = [base64.b64encode(x[4]) for x in data]
        imgs = [x.decode('utf-8') for x in imgs]

        for i in range(len(data)):
            data[i][4] = imgs[i]
        data.extend(data1)
        data.sort(key=lambda x: x[1], reverse=True)

        return jsonify({"htmlresponse": render_template('response.html', data=data)})

    elif request.method == "POST":
        mycursor.execute("select id,tag from eventags")
        tvalue = mycursor.fetchall()
        tvalue = [(x[0], x[1]) for x in tvalue]
        tvalue = dict(tvalue)
        tvalue[0] = ''
        x = request.form['tag']
        x = tvalue.get(int(x))
        if x:
            mycursor.execute(
                " select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id from postss as po , newprofile as p"
                " where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date".format(
                    str(x)))
            data = mycursor.fetchall()
            mycursor.execute(
                " select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3,po.id from post as po , newprofile as p"
                " where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date".format(
                    str(x)))
            data1 = mycursor.fetchall()
            data = [list(x) for x in data]
            imgs = [base64.b64encode(x[4]) for x in data]
            imgs = [x.decode('utf-8') for x in imgs]
            for i in range(len(data)):
                data[i][4] = imgs[i]
            data.extend(data1)
            data.sort(key=lambda x: x[1], reverse=True)
            return jsonify({"htmlresponse": render_template('response.html', data=data)})

        else:
            return jsonify({"error": "Select a tag "})

    return jsonify({"error": "error"})

#route to create post
@app.route('/create_post', methods = ['GET','POST'])
def create_post():
    ptform = PosttForm()
    mycursor.execute("select id,tag from eventags")
    value = mycursor.fetchall()
    value = [(x[0], x[1]) for x in value]
    value = sorted(value)
    ptform.tag1.choices = value
    ptform.tag2.choices = value
    ptform.tag3.choices = value
    value = dict(value)
    value[0] = ''
    if request.method == "POST":
        if ptform.validate_on_submit():
            f = request.files['post_img']
            mycursor.execute("update eventags set count=count+1 where id='{0}'".format(ptform.tag1.data))
            connection.commit()
            if ptform.tag2.data != 0:
                mycursor.execute("update eventags set count=count+1 where id='{0}'".format(ptform.tag2.data))
                connection.commit()
            if ptform.tag3.data != 0:
                mycursor.execute("update eventags set count=count+1 where id='{0}'".format(ptform.tag3.data))
                connection.commit()
            if f:
                newPost = Postss(d=ptform.date.data, pd=ptform.post_description.data,
                                 t1=value[ptform.tag1.data], t2=value[ptform.tag2.data], t3=value[ptform.tag3.data],
                                 mid=current_user.mail_id
                                 , pi=f.read())
            else:
                newPost = post(d=ptform.date.data, pd=ptform.post_description.data,
                               t1=value[ptform.tag1.data], t2=value[ptform.tag2.data], t3=value[ptform.tag3.data],
                               mid=current_user.mail_id
                               , pi=f.read())

            db.session.add(newPost)
            db.session.commit()
            return "uploaded successfully"
    return render_template('create_post.html', form=ptform)

#route to like or dislike a post
@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):  
   
    if action == 'like': ## if the post is liked
        current_user.like_post(post_id) ## call like_post in models to include the post in post_like table

    if action == 'unlike': ## if the post is disliked
        current_user.unlike_post(post_id) ## call unlike_post in models to delete the post in post_like table

    return redirect(request.referrer) ## return to the same page

#route to report or take back report of a post and auto delete a post if many people reported 
@app.route('/report/<int:post_id>/<action>') 
@login_required
def report_action(post_id, action):
    print(post_id)
    if action == 'report': ## if the post is reported
        current_user.report_post(post_id) ## call report_post in models to include the post in post_report table
        mycursor.execute("select id, user_id from post_report where post_id = {0} ".format(post_id)) ## fetching all users and ids  who reported the post
        reports = mycursor.fetchall() 
        reports = [x[0] for x in reports] ## getting users
        no_of_reports = len(reports) ##counting number of users who reported the post
        print(no_of_reports) 
        if no_of_reports>1 : ## if no of reports crosses a threshold value
            mycursor.execute("delete from postss where id = {0}".format(post_id)) ## delete the post if no of reports crosses a threshold value
            connection.commit() ## commit the changes to database 
    if action == 'unreport': ## if a report on post is  taken back
        current_user.unreport_post(post_id) ## call unreport_post in models to delete the post in post_report table

    return redirect(request.referrer)## return to the same page



@app.route('/calendar', methods=["GET", "POST"])
def calendar():
    mycursor.execute("select * from events order by id") # selecting all the event data form database
    data = mycursor.fetchall()
    timedate1 = [datetime.datetime.combine(x[5], x[6]) for x in data] # combining the start date and time of every event
    timedate2 = [datetime.datetime.combine(x[7], x[8]) for x in data] # combining the end date and time of every event
    data = [list(x) for x in data]

    for i in range(len(data)):
        data[i][5] = timedate1[i] #replacing the value with combined start date and time event.
        data[i][6] = timedate2[i] #replacing the value with  end date and time event.

    return render_template("calendar1.html", data=data)

@app.route("/addevent", methods=['GET', 'POST'])
def addevent():
    eform = EventForm()
    mycursor.execute("select tag from eventags")
    value = mycursor.fetchall()
    value = [x[0] for x in value]
    if request.method == 'POST':

        if eform.tag.data not in value:
            x = 0
            newtag = eventags(t = eform.tag.data, c=x)
            db.session.add(newtag)
            db.session.commit()

        newevents = events(t=eform.title.data, d=eform.description.data, v=eform.venue.data, tag=eform.tag.data,
                           sd=eform.sdate.data,
                           st=eform.stime.data, ed=eform.edate.data, et=eform.etime.data, un=current_user.mail_id,
                           c=eform.color.data)
        db.session.add(newevents)
        db.session.commit()
        return "success"
    return render_template('create_event.html', form=eform)

# logout route
@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()   # inbuilt function to logout user
    return redirect(url_for('login')) # redirect to login page
