from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField  ,SelectField,TimeField
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
    tag1 = SelectField("tag1", coerce=int, validators=[InputRequired()],default=None)
    tag2 = SelectField("tag2", coerce=int,default=None)
    tag3 = SelectField("tag3", coerce=int,default=None)
    date = DateField("date",format='%Y-%m-%d')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.date.data:
            self.date.data = datetime.date.today()



class HomeForm(FlaskForm):
    tag_search = SelectField('enter the tag : ',coerce=int,validators=[InputRequired()])

class UpdateYourAccountForm(FlaskForm):
    mail_id = StringField('mail_id')  #validators=[invalid_mail,InputRequired(message="Mail already exists")], check this
    full_name = StringField('full_name')
    year = IntegerField('year')
    department = StringField('department')
    degree = StringField('degree')
    image_file = FileField("upload")
    submit = SubmitField('Update')


class EventForm(FlaskForm):
    title = StringField("Title",validators=[InputRequired()])
    description = StringField("Description",validators=[InputRequired()])
    venue      = StringField("Venue",validators=[InputRequired()])
    sdate     = DateField("Start Date",format='%Y-%m-%d',validators=[InputRequired()])
    stime     = TimeField("Start Time", format="%H:%M",validators=[InputRequired()])
    edate = DateField("End Date", format='%Y-%m-%d',validators=[InputRequired()])
    etime = TimeField("End Time", format="%H:%M",validators=[InputRequired()])
    tag   = StringField("Tag",validators=[InputRequired()])