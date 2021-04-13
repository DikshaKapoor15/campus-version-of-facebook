from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect,request, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine
from flask_mail import Mail, Message  ##to be checked
from base64 import b64encode
from app.email import *
from itsdangerous import URLSafeTimedSerializer ##to be checked

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

##mail section to be checked
mail= Mail(app)

# mail details from which mail to be sent
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

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Credentials.query.filter_by(mail_id=form.email.data).first()
        if user:
            print("user found")
            send_password_reset_email(user)
        #flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    idRec = Credentials.verify_reset_password_token(token)
    print("heyyyyyyappplication""", idRec)
    # if not user:
    #     return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = Credentials.query.filter_by(mail_id=idRec).first()
        print("heyy after reset password", user.id)
        print("heyy before reset password", user.password)
        user.password=form.password.data

        mycursor.execute("UPDATE credentials SET password = '{password}' WHERE mail_id = '{mail}' ".format(password = str(user.password), mail =  str(idRec)))
        connection.commit()
        # user1 = Credentials.query.filter_by(mail_id=idRec).first()
        print("heyy after reset password in database", user.password)
        #flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/home',methods=["POST","GET"])
def home():

    hform=HomeForm()
    return render_template('home.html', form=hform)

@app.route('/homeSearch',methods=["POST","GET"])
def homeSearch():

    #print("f2")
    if request.method == "GET":
        mycursor.execute("select distinct  p.full_name, po.date,po.post_description,po.tag1,po.tag2,po.tag3 from posts as po , profile as p where p.mail_id=po.mail_id order by po.date desc")
        data = mycursor.fetchall()
        #print(data)
        mycursor.execute("SELECT distinct p.id, pr.full_name, p.post_description, p.date, p.post_img, p.tag1, p.tag2, p.tag3 FROM postss as p, profile as pr where pr.mail_id = p.mail_id order by p.date desc")
        data1 = mycursor.fetchall()
        #print(data1)
        data1 = [list(x) for x in data1]
        imgs = [b64encode(x[4]) for x in data1]
        imgs = [x.decode('utf-8') for x in imgs]
        for i in range(len(data1)):
            data1[i][4]=imgs[i]
        return jsonify({"htmlresponse": render_template('response.html', data1=data1, data = data )})
    elif request.method == "POST":
        x=request.form['tag']
        mycursor.execute(" select distinct  p.full_name, po.date,po.post_description,po.tag1,po.tag2,po.tag3 from posts as po , profile as p where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}') order by date desc".format(str(x)))
        data=mycursor.fetchall()
        mycursor.execute(" select distinct po.id, p.full_name, po.post_description,po.date,po.post_img,po.tag1,po.tag2,po.tag3 from postss as po , profile as p where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date desc".format(str(x)))
        data1 = mycursor.fetchall()
        data1 = [list(x) for x in data1]
        imgs = [b64encode(x[4]) for x in data1]
        imgs = [x.decode('utf-8') for x in imgs]
        for i in range(len(data1)):
            data1[i][4] = imgs[i]
        print(data1)
        return jsonify({"htmlresponse": render_template('response.html',data=data, data1 =data1)})
    return jsonify({"error":"500 400 401"})

@app.route('/create_post', methods = ['GET','POST'])
def create_post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        newpost = Posts(mail_id = current_user.mail_id, date = post_form.post_date.data, post_description = post_form.post_description.data, tag1 = post_form.tag1.data, tag2 = post_form.tag2.data, tag3 = post_form.tag3.data )
        db.session.add(newpost)
        db.session.commit()
        return "submited successfully"
    return render_template('post.html',form = post_form)

@app.route('/calendar',methods=["GET","POST"])
def calendar():
    mycursor.execute("select * from events order by id")
    data= mycursor.fetchall()
    timedate1 =[datetime.datetime.combine(x[2],x[4]) for x in data ]
    timedate2 = [datetime.datetime.combine(x[3],x[5]) for x in data]
  #  print(timedate1,timedate2,sep="\n")
    data = [list(x) for x in data]
   # print(data)
    for i in range(len(data)):
        data[i].pop()
        data[i].pop()
        data[i].pop()
        data[i].pop()
        data[i].append(timedate1[i])
        data[i].append(timedate2[i])
    print(data)
    return render_template("calendar1.html",data=data)

# logout route
@app.route("/logout", methods=['GET'])
def logout():
    logout_user() # inbuilt function to logout user
    return redirect(url_for('login')) # redirect to login page

