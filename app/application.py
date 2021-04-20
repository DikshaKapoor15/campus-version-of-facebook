from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect, request, jsonify, Response
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine
import base64
from flask_bootstrap import Bootstrap
import datetime

engine = create_engine(
    'postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk')
connection = engine.raw_connection()
mycursor = connection.cursor()
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login = LoginManager(app)
login.init_app(app)
Bootstrap(app)


@login.user_loader
def load_user(id):
    return Credentials.query.get(int(id))


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    reg_form = RegistrationForm()
    print(request.method)
    if request.method == 'POST':
        if request.form["action"] == "Login":
            if login_form.validate_on_submit():
                user_object = Credentials.query.filter_by(mail_id=login_form.mail_id.data).first()
                login_user(user_object)

                return "logged in"
        elif request.form["action"] == "Register":
            if reg_form.validate_on_submit():
                mail_id = reg_form.mail_id.data
                password = reg_form.password.data
                cred = Credentials(mail_id=mail_id, password=password)
                prof = Profile(mail_id=mail_id, full_name=reg_form.full_name.data, year=reg_form.year.data,
                               department=reg_form.department.data, degree=reg_form.degree.data)
                db.session.add(cred)
                db.session.add(prof)
                db.session.commit()
                return redirect(url_for('login'))
    return render_template("login.html", form1=login_form, form=reg_form)


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


@app.route('/home', methods=["POST", "GET"])
def home():
    hform = HomeForm()
    mycursor.execute("select id,tag from eventags")
    value = mycursor.fetchall()
    value = [(x[0], x[1]) for x in value]
    value = sorted(value)
    hform.tag_search.choices = value
    return render_template('home.html', form=hform)


@app.route('/homeSearch', methods=["POST", "GET"])
def homeSearch():
    mycursor.execute("select tag from eventags order by count desc")
    trending = mycursor.fetchall()
    trending = [x[0] for x in trending]
    trending = trending[:3]

    if request.method == "GET":
        print("1111")
        mycursor.execute(
            "select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3 from post as po , profile as p where p.mail_id=po.mail_id order by date")
        data1 = mycursor.fetchall()
        print("2222")
        mycursor.execute(
            "select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3 from postss as po , profile as p where p.mail_id=po.mail_id order by date")
        data = mycursor.fetchall()
        data = [list(x) for x in data]
        imgs = [base64.b64encode(x[4]) for x in data]
        imgs = [x.decode('utf-8') for x in imgs]

        for i in range(len(data)):
            data[i][4] = imgs[i]
        data.extend(data1)
        data.sort(key=lambda x: x[1], reverse=True)
        print(data1)
        print(list([x[1] for x in data]))
        return jsonify({"htmlresponse": render_template('view.html', data=data, trending=trending)})

    elif request.method == "POST":
        mycursor.execute("select id,tag from eventags")
        tvalue = mycursor.fetchall()
        tvalue = [(x[0], x[1]) for x in tvalue]
        tvalue = dict(tvalue)
        tvalue[0] = ''
        x = request.form['tag']
        x = tvalue.get(int(x))
        if int(x):
            mycursor.execute(
                " select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3 from postss as po , profile as p"
                " where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date".format(
                    str(x)))
            data = mycursor.fetchall()
            mycursor.execute(
                " select distinct  p.full_name, po.date,po.post_description,po.tag1,po.post_img,po.tag2,po.tag3 from post as po , profile as p"
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
            return jsonify({"htmlresponse": render_template('view.html', data=data, trending=trending)})

        else:
            return jsonify({"error": "Select a tag "})

    return jsonify({"error": "error"})


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
