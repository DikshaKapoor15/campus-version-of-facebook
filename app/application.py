from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect,request, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine

engine = create_engine('postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk')
connection = engine.raw_connection()
mycursor = connection.cursor()
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk"
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
def temp():
    return render_template("index.html")
@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_object = Credentials.query.filter_by(mail_id = login_form.mail_id.data).first()
        login_user(user_object)

        return redirect(url_for('home', userdata = login_form.username.data))
    return render_template("login.html", form=login_form)

@app.route('/register',methods=['GET','POST'])
def register():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        mail_id = reg_form.mail_id.data
        password = reg_form.password.data
        cred = Credentials(mail_id = mail_id , password=password)
        prof = Profile(mail_id = mail_id, full_name = reg_form.full_name.data, year = reg_form.year.data, department = reg_form.department.data, degree = reg_form.degree.data)
        db.session.add(cred)
        db.session.add(prof)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("register.html",form = reg_form)



