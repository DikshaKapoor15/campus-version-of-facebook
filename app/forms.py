from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField  ,SelectField
from wtforms.validators import InputRequired, ValidationError
from flask_wtf.file import FileField, FileRequired
from app.models import *
import datetime

def invalid_credentials(form,field):
    mail_id_entered = form.mail_id.data
    password_entered = field.data
    user_object = Credentials.query.filter_by(mail_id = mail_id_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif password_entered!=user_object.password:
        raise ValidationError("Username or password is incorrect")

def invalid_mail(form,field):
    mail_id_entered = form.mail_id.data
    user_object = Credentials.query.filter_by(mail_id=mail_id_entered).first()
    if user_object:
        raise ValidationError("Email already exists.")


def invalid_password(form,field):
    password_entered = field.data
    password_re_entered = form.confirm_password.data
    if password_entered != password_re_entered:
        raise ValidationError("Passwords entered don't match")

class LoginForm(FlaskForm):
    mail_id = StringField('mail_id', validators=[InputRequired(message = "Username required")])
    password = PasswordField('Password', validators=[InputRequired(message = "Password required"),invalid_credentials])


class RegistrationForm(FlaskForm):
    mail_id = StringField('mail_id',validators=[InputRequired(message = "Mail already exists"), invalid_mail])
    password = PasswordField('password',validators=[InputRequired(message = "Password mismatch"),invalid_password])
    confirm_password = PasswordField('confirm_password')
    full_name = StringField('full_name')
    year = IntegerField('year')
    department = StringField('department')
    degree = StringField('degree')



class PosttForm(FlaskForm):
    post_description = StringField('caption')
    post_img = FileField("upload")
    tag1 = StringField("tag1",validators=[InputRequired()])
    tag2 = StringField("tag2")
    tag3 = StringField("tag3")
    date = DateField("date",format='%Y-%m-%d')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.date.data:
            self.date.data = datetime.date.today()

class PostForm(FlaskForm):
    mail_id = StringField('mail_id')
    post_date = DateField(format='%Y-%m-%d')
    post_description = StringField('post_description')
    tag1 = StringField('tag1')
    tag2 = StringField('tag2')
    tag3 = StringField('tag3')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.post_date.data:
            self.post_date.data = datetime.date.today()


class HomeForm(FlaskForm):
    tag_search = StringField('enter the tag : ')