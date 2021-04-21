from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect,request, jsonify, Response
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine
from flask_mail import Mail, Message  ##to be checked
from base64 import b64encode
from app.email import *
from itsdangerous import URLSafeTimedSerializer ##to be checked
from flask_bootstrap import Bootstrap
import datetime

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

db = SQLAlchemy(app)
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# session = db.session()
# cursor = session.execute(sql).cursor

login = LoginManager(app)
login.init_app(app)
Bootstrap(app)

mail= Mail(app)

# configuring the mail details from which mail is to be sent
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'developmentsoftware305@gmail.com'
app.config['MAIL_PASSWORD'] = 'tempmail1@'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

#logging in user
@login.user_loader
def load_user(id):
    return Credentials.query.get(int(id))

#home route
@app.route('/', methods=['GET', 'POST'])
    
#login and register route
@app.route('/login', methods = ['GET','POST'])
def login():
    login_form = LoginForm() # loading login form
    reg_form = RegistrationForm() #loading register form
    print(request.method)
    if request.method == 'POST': # if form submitted
        if request.form["action"] == "Login": # if login form submitted
            if login_form.validate_on_submit(): # if conditions specified in forms.py are satisfied
                user_object = Credentials.query.filter_by(mail_id = login_form.mail_id.data).first() # get details from Credentials table
                login_user(user_object) #login the particular user

                return redirect(url_for('home')) # redirect to home page after successful login
        elif request.form["action"] == "Register": # if registration form submitted
            if reg_form.validate_on_submit(): # if conditions specified in forms.py are satisfied
                mail_id = reg_form.mail_id.data # get details from the form submitted
                password = reg_form.password.data
                cred = Credentials(mail_id=mail_id, password=password) # create object for Credentials
                prof = Profile(mail_id=mail_id, full_name=reg_form.full_name.data, year=reg_form.year.data,
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
            send_password_reset_email(user)      #if user is found, invoke send_password function defined in models corr to the user mail
        # flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))        #redirect to login page
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


#when the user clicks on the password reset link , a second route associated with password reset is triggered
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #retreiving the user by invoking verify_reset_token_method
    idRec = Credentials.verify_reset_password_token(token)

    # if not user:
    #     return redirect(url_for('login'))    #to be checked not required yet

    #if token is valid the user is presented with aform to reset password
    form = ResetPasswordForm()
    # if form details are valid
    if form.validate_on_submit():
        user = Credentials.query.filter_by(mail_id=idRec).first()  #fetch the user from database for updation
        print("heyy after reset password", user.password)
        print("heyy before reset password", user.password)  ##for personal convenience

        user.password=form.password.data  #reseting the users password to one retreived from form

        #update query
        mycursor.execute("UPDATE credentials SET password = '{password}' WHERE mail_id = '{mail}' ".format(password = str(user.password), mail =  str(idRec)))
        connection.commit()

        print("heyy after reset password in database", user.password)
        #flash('Your password has been reset.')
        return redirect(url_for('login'))       #finally redirect to login page

    return render_template('reset_password.html', form=form)    #rendering corresponding template with password reset form

@app.route('/home',methods=["POST","GET"])
def home():
    hform=HomeForm() #loading of home form from forms.py
    return render_template('home.html', form=hform) 

#re-directed to homeSearch route by url present in ajax in home.html
@app.route('/homeSearch',methods=["POST","GET"])
def homeSearch():  
    if request.method == "GET": # if no tag is searched method is GET 
        # query to select all posts in database ordered by post date  without images
        mycursor.execute("select distinct  p.full_name, po.date,po.post_description,po.tag1,po.tag2,po.tag3 from posts as po , profile as p where p.mail_id=po.mail_id order by po.date desc")
        # query returns list of tuples containing fullname of the user(posted the post), post dated , post description , tags  of all posts
        data = mycursor.fetchall()
        # query to select all posts in database ordered by post date  with images
        mycursor.execute("SELECT distinct p.id, pr.full_name, p.post_description, p.date, p.post_img, p.tag1, p.tag2, p.tag3 FROM postss as p, profile as pr where pr.mail_id = p.mail_id order by p.date desc")
        # query returns list of tuples containing post id,fullname of the user(posted the post), post dated , post description , tags ,image of all posts
        data1 = mycursor.fetchall()
        data1 = [list(x) for x in data1] # converting tuples to lists
        imgs = [b64encode(x[4]) for x in data1] # encoding binary image data into ascii strings using base46 library
        imgs = [x.decode('utf-8') for x in imgs] # decoding to binary data to view image
        for i in range(len(data1)):
            data1[i][4]=imgs[i]  # replacing image with view able image
        return jsonify({"htmlresponse": render_template('response.html', data1=data1, data = data )}) # response.html consists of post templates and data is passed to th html page for viewing.
    
    elif request.method == "POST": # if any tag is searched
        x=request.form['tag']      # tag searched is saved in variable x and data is requested from ajax function in home.html
        # query to select all posts related to tag from database ordered by post date  without images
        mycursor.execute(" select distinct  p.full_name, po.date,po.post_description,po.tag1,po.tag2,po.tag3 from posts as po , profile as p where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}') order by date desc".format(str(x)))
         # query returns list of tuples containing fullname of the user(posted the post), post dated , post description , tags  of all posts
        data=mycursor.fetchall()
        # query to select all posts related to tag from database ordered by post date  with images
        mycursor.execute(" select distinct po.id, p.full_name, po.post_description,po.date,po.post_img,po.tag1,po.tag2,po.tag3 from postss as po , profile as p where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date desc".format(str(x)))
        # query returns list of tuples containing post id,fullname of the user(posted the post), post dated , post description , tags ,image of all posts
        data1 = mycursor.fetchall()
        data1 = [list(x) for x in data1] # converting tuples to lists
        imgs = [b64encode(x[4]) for x in data1] # encoding binary image data into ascii strings using base46 library
        imgs = [x.decode('utf-8') for x in imgs] # decoding to binary data to view image
        for i in range(len(data1)):
            data1[i][4] = imgs[i]    # replacing image with view able image
        return jsonify({"htmlresponse": render_template('response.html',data=data, data1 =data1)})# response.html consists of post templates and data is passed to th html page for viewing.
    return jsonify({"error":"500 400 401"})

@app.route('/create_post', methods = ['GET','POST'])
def create_post():
    post_form = PostForm() # loading post form
    if post_form.validate_on_submit(): # if validators on the form are true
        newpost = Posts(mail_id = current_user.mail_id, date = post_form.post_date.data, post_description = post_form.post_description.data, tag1 = post_form.tag1.data, tag2 = post_form.tag2.data, tag3 = post_form.tag3.data ) # creating posts object
        db.session.add(newpost)
        db.session.commit() # adding data to posts table in database
        return "submited successfully"
    return render_template('post.html',form = post_form) # return post form if get method
@app.route('/posts', methods=["POST", "GET"])
def posts():
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
    return render_template('postt.html', form=ptform)


# @app.route('/calendar',methods=["GET","POST"])
# def calendar():
#     # selecting all the event data form database
#     mycursor.execute("select * from events order by id")
#     data= mycursor.fetchall()
#     timedate1 =[datetime.datetime.combine(x[2],x[4]) for x in data ] # combining the start date and time of every event
#     timedate2 = [datetime.datetime.combine(x[3],x[5]) for x in data]  # combining the end date and time of every event
#     data = [list(x) for x in data] # converting tuples into lists
#     for i in range(len(data)):
#         data[i].pop() # poping the end time
#         data[i].pop() # poping start time
#         data[i].pop() # poping end date
#         data[i].pop() # poping the start date
#         data[i].append(timedate1[i]) # appending the combined start date and time event.
#         data[i].append(timedate2[i]) # appending the combined end date and time of an event.
#
#     return render_template("calendar1.html",data=data) # return calendar

@app.route('/calendar', methods=["GET", "POST"])
def calendar():
    mycursor.execute("select * from events order by id")
    data = mycursor.fetchall()
    timedate1 = [datetime.datetime.combine(x[5], x[6]) for x in data]
    timedate2 = [datetime.datetime.combine(x[7], x[8]) for x in data]
    data = [list(x) for x in data]

    for i in range(len(data)):
        data[i][5] = timedate1[i]
        data[i][6] = timedate2[i]

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
            newtag = eventags(t=eform.tag.data, c=x)
            db.session.add(newtag)
            db.session.commit()

        newevents = events(t=eform.title.data, d=eform.description.data, v=eform.venue.data, tag=eform.tag.data,
                           sd=eform.sdate.data,
                           st=eform.stime.data, ed=eform.edate.data, et=eform.etime.data, un=current_user.mail_id)
        db.session.add(newevents)
        db.session.commit()
        return "success"
    return render_template('event.html', form=eform)


# logout route
@app.route("/logout", methods=['GET'])
def logout():
    logout_user() # inbuilt function to logout user
    return redirect(url_for('login')) # redirect to login page

