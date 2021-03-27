from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect,request, jsonify,abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine
from flask_mail import Mail, Message  ##to be checked
from app.email import *
from itsdangerous import URLSafeTimedSerializer ##to be checked

engine = create_engine('postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk')
connection = engine.raw_connection()
mycursor = connection.cursor()
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

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'kanikakapoor11995@gmail.com'
app.config['MAIL_PASSWORD'] = 'Ilovemyself@1506'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


def send_email(user_mail, subject, html):
   print("hellooohterre")
   msg = Message("Hello", sender = "kanikakapoor11995@gmail.com", recipients = ["kanikakapoor11995@gmail.com"])
   msg.body = html
   mail.send(msg)
   return "Sent"



@login.user_loader
def load_user(id):
    return Credentials.query.get(int(id))


# @app.route('/', methods=['GET', 'POST'])
# def wel()
    
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
    try:
        idRec = Credentials.verify_reset_password_token(token)
        print("heyyyyyyappplication""", idRec)
        if not idRec:
           return redirect(url_for('login'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            user = Credentials.query.filter_by(mail_id=idRec).first()
            print("heyy before reset password", user.mail_id)
            print("heyy before reset password", user.password)
            user.password = form.password.data
            #db.session.add(user)
            db.session.commit()
            # sql = " UPDATE credentials SET password = %s WHERE mail_id = %s"
            # mycursor.execute(sql, (user.password, idRec))

            # user1 = Credentials.query.filter_by(mail_id=idRec).first()
            #print("heyy after reset password in database", user.password)
            #flash('Your password has been reset.')

            return redirect(url_for('login'))
    except Exception as e:
        print("Couldn't update the password")
        print(e)

    return render_template('reset_password.html', form=form)



