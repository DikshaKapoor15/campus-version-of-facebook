from app import app
from app.forms import *
from app.models import *
from flask import render_template, url_for, redirect, request, jsonify, abort, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import create_engine
from flask_mail import Mail, Message  ##to be checked
from app.email import *
from itsdangerous import URLSafeTimedSerializer ##to be checked
import os
import secrets
from PIL import Image

engine = create_engine('postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk')
connection = engine.raw_connection()
mycursor = connection.cursor()
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://odebgxxluzxqto:02911cc1fe5c97f0916d6a05760b41704668ab6013b712674a3b677f127ac1db@ec2-54-205-183-19.compute-1.amazonaws.com:5432/db0511lmef59sk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# session = db.session()
# cursor = session.execute(sql).cursor

login = LoginManager(app)
login.init_app(app)

##mail section to be checked
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'developmentsoftware305@gmail.com'
app.config['MAIL_PASSWORD'] = 'tempmail1@'

app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


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

                return redirect(url_for('create_post'))
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


@app.route('/create_post', methods = ['GET','POST'])
def create_post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        newpost = Posts(mail_id = current_user.mail_id, date = post_form.post_date.data, post_description = post_form.post_description.data, tag1 = post_form.tag1.data, tag2 = post_form.tag2.data, tag3 = post_form.tag3.data )
        db.session.add(newpost)
        db.session.commit()
        return "submited successfully"
    return render_template('post.html',form = post_form)

#################for updating profile####################################

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)  ###for resizing
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/updateAccount', methods=['GET', 'POST'])
# @login_required    to be checked
def updateAccount():
    form = UpdateYourAccountForm()
    if form.validate_on_submit():
        picture_file=" "
        if form.image_file.data:
            picture_file = save_picture(form.image_file.data)
            # current_user.image_file = picture_file  to be checkeddd
        # image_file=picture_file
        ###yet to be seen
        mail_id = form.mail_id.data
        if mail_id!= current_user.mail_id:
                user = Profile.query.filter_by(mail_id=mail_id).first()
                if user:
                    raise ValidationError('That email is taken. Please choose a different one.')
        ##to be seen
        full_name = form.full_name.data
        prof = Profile(full_name=form.full_name.data, year=form.year.data,
                       department=form.department.data, degree=form.degree.data, mail_id=mail_id, image_file=picture_file)
        mycursor.execute("UPDATE profile SET full_name= '{fullName}', year='{year}', department='{dept}', degree='{degree}', mail_id='{mail}' WHERE mail_id = '{mailId}' ".format(fullName=str(form.full_name.data),year=int(form.year.data), dept=str(form.department.data),degree=str(form.degree.data), mail=str(form.mail_id.data), mailId=str(current_user.mail_id)))
        mycursor.execute("UPDATE credentials SET mail_id = '{mail}' WHERE mail_id = '{mailId}' ".format(mail=str(form.mail_id.data), mailId=str(current_user.mail_id)))
        connection.commit()
        ### THIS UPDATING INFO TO BE SEEN YET
        flash('Your account has been updated!', 'success')
        return redirect(url_for('create_post'))    #redirection to be seennn

    elif request.method == 'GET':
         # form.full_name.data = current_user.full_name
         user = Profile.query.filter_by(mail_id=current_user.mail_id).first()   ###nothing done for error
         #others fields to be added yet
         form.mail_id.data = user.mail_id
         form.full_name.data=user.full_name
         form.year.data = user.year
         form.department.data=user.department
         form.degree.data = user.degree




    # imagefile = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('updateAccount.html', title='Account',form=form)

     ##image_file to be passed yet

@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    return "you are logged out"