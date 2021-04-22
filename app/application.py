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


@app.route('/', methods=['GET', 'POST'])
    
@app.route('/login', methods = ['GET','POST'])
def login():
    login_form = LoginForm()
    reg_form = RegistrationForm()
    print(request.method)
    if request.method == 'POST':
        if request.form["action"] == "Login":
            if login_form.validate_on_submit():
                user_object = Credentials.query.filter_by(mail_id = login_form.mail_id.data).first()
                login_user(user_object)

                return redirect(url_for('home'))
        elif request.form["action"] == "Register":
            if reg_form.validate_on_submit():
                mail_id = reg_form.mail_id.data
                password = reg_form.password.data
                cred = Credentials(mail_id=mail_id, password=generate_password_hash(password))
                prof = newprofile(mail_id=mail_id, full_name=reg_form.full_name.data, year=reg_form.year.data,
                               department=reg_form.department.data, degree=reg_form.degree.data)
                db.session.add(cred)
                db.session.add(prof)
                db.session.commit()
                return redirect(url_for('login'))
    return render_template("login.html", form1 = login_form, form = reg_form)

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
        user.password=generate_password_hash(form.password.data)

        mycursor.execute("UPDATE credentials SET password = '{password}' WHERE mail_id = '{mail}' ".format(password = str(user.password), mail =  str(idRec)))
        connection.commit()
        # user1 = Credentials.query.filter_by(mail_id=idRec).first()
        print("heyy after reset password in database", user.password)
        #flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/home',methods=["POST","GET"])
def home():
    mycursor.execute("select tag from eventags order by count desc")
    trending = mycursor.fetchall()
    trending = [x[0] for x in trending]
    trending = trending[:4]
    print(trending)
    hform = HomeForm()
    mycursor.execute("select id,tag from eventags")
    value = mycursor.fetchall()
    value = [(x[0], x[1]) for x in value]
    value = sorted(value)
    hform.tag_search.choices = value
    return render_template('home.html', form=hform,trending=trending)


@app.route('/fetchdata',methods=["POST","GET"])
def fetchdata():
    if request.method=="POST":
        id=request.form['id']
        mycursor.execute("select * from events where events.tag = '{0}'".format(str(id)))
        events = mycursor.fetchall()
        print(id)
    return jsonify({'htmlresponse':render_template('response1.html',event = events)})


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

@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    print(post_id)
    if action == 'like':
        current_user.like_post(post_id)

    if action == 'unlike':
        current_user.unlike_post(post_id)

    return redirect(request.referrer)

@app.route('/report/<int:post_id>/<action>')
@login_required
def report_action(post_id, action):
    print(post_id)
    if action == 'report':
        current_user.report_post(post_id)
        mycursor.execute("select id, user_id from post_report where post_id = {0} ".format(post_id))
        reports = mycursor.fetchall()
        reports = [x[0] for x in reports]
        no_of_reports = len(reports)
        print(no_of_reports)
        if no_of_reports>1 :
            mycursor.execute("delete from postss where id = {0}".format(post_id))
            connection.commit()
    if action == 'unreport':
        current_user.unreport_post(post_id)

    return redirect(request.referrer)



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

@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
