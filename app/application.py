from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect,request, jsonify ,Response
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine
from base64 import b64encode
#import Image
import io
from werkzeug.utils import secure_filename


engine = create_engine('postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk')
connection = engine.raw_connection()
mycursor = connection.cursor()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# session = db.session()
# cursor = session.execute(sql).cursor

login = LoginManager(app)
login.init_app(app)


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
    return render_template("login.html", form1 = login_form, form = reg_form)

@app.route('/postt', methods=["POST","GET"] )
def postt():
    ptform = PosttForm()
    if request.method == "POST":
        if ptform.validate_on_submit():
            f = request.files['post_img']
            #print(f.read())
            newPost = Postss(d=ptform.date.data , pd = ptform.post_description.data ,
                            t1=ptform.tag1.data,t2=ptform.tag2.data,t3=ptform.tag3.data,mid=current_user.mail_id
                            ,pi=f.read())
            db.session.add(newPost)
            db.session.commit()
            return "uploaded successfully"
    return render_template('postt.html',form=ptform)


@app.route('/post',methods=["POST","GET"])
def post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        newpost = Posts(mail_id=current_user.mail_id, date=post_form.post_date.data,
                        post_description=post_form.post_description.data, tag1=post_form.tag1.data,
                        tag2=post_form.tag2.data, tag3=post_form.tag3.data)
        db.session.add(newpost)
        db.session.commit()
        return "submited successfully"
    return render_template('post.html', form=post_form)


@app.route('/home',methods=["POST","GET"])
def home():

    hform=HomeForm()
    return render_template('home.html', form=hform)

@app.route('/homeSearch',methods=["POST","GET"])
def homeSearch():

    #print("f2")
    if request.method == "GET":
       # mycursor.execute("select distinct  p.full_name, po.date,po.post_description,po.tag1,po.tag2,po.tag3 from posts as po , profile as p where p.mail_id=po.mail_id order by date")
       # data = mycursor.fetchall()
        #print(data)
        mycursor.execute("SELECT * FROM postss")
        data = mycursor.fetchall()
      #  print(data)
        data = [list(x) for x in data]
        imgs = [b64encode(x[4]) for x in data]
        imgs = [x.decode('utf-8') for x in imgs]
        for i in range(len(data)):
            data[i][4]=imgs[i]
       # print(data)
        return jsonify({"htmlresponse": render_template('view.html', data=data )})
    elif request.method == "POST":
        x=request.form['tag']
        mycursor.execute(" select distinct  p.full_name, po.date,po.post_description,po.tag1,po.tag2,po.tag3 from postss as po , profile as p"
                         " where (p.mail_id=po.mail_id) and (po.tag1='{0}' or po.tag2='{0}' or po.tag3='{0}')  order by date".format(str(x)))
        data=mycursor.fetchall()
        data = [list(x) for x in data]
        imgs = [b64encode(x[4]) for x in data]
        imgs = [x.decode('utf-8') for x in imgs]
        for i in range(len(data)):
            data[i][4] = imgs[i]
       # print(data)
        return jsonify({"htmlresponse": render_template('view.html',data=data)})
    return jsonify({"error":"500 400 401"})

@app.route('/view',methods=["POST","GET"])
def view():
    mycursor.execute("SELECT * FROM postss")
    data=mycursor.fetchall()
   # print(data)
    imgs = [b64encode(x[4]) for x in data]
    imgs = [x.decode('utf-8') for x in imgs]

    return render_template('view.html',imgs=imgs)
   # r = Response(imgs[0])
   # r.headers['Content-Type'] = 'text/xml; charset=utf-8'
   # return r

