from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField,SelectField,TimeField
from wtforms.validators import InputRequired, ValidationError,DataRequired, EqualTo ,Email
from flask_wtf.file import FileField, FileRequired
from app.models import *
import datetime
import re

# validators for credentials while login
def invalid_credentials(form,field):
    mail_id_entered = form.mail_id.data # getting data from form
    password_entered = field.data
    user_object = Credentials.query.filter_by(mail_id = mail_id_entered).first() # searching credentials in database
    if user_object is None:  # if not found invalid credentials
        raise ValidationError("Username or password is incorrect") 
    elif password_entered!=user_object.password: # if password incorrect invalid credentials
        raise ValidationError("Username or password is incorrect")


# validators for mail while registration
def invalid_mail(form,field):
    mail_id_entered = form.mail_id.data # getting data from form
    user_object = Credentials.query.filter_by(mail_id=mail_id_entered).first()# searching credentials in database
    if user_object: # if already a mail found in database then invalid registraion
        raise ValidationError("Email already exists.")


# validators for password while registration
def invalid_password(form,field):
    password_entered = field.data # getting data from form
    password_re_entered = form.confirm_password.data
    if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password_entered):# password should follow certain rules to be valid. These rules are coded in regular expressions
        raise ValidationError("At least 8 characters, Must be restricted to, though does not specifically require any of: uppercase letters: A-Z, lowercase letters: a-z, numbers: 0-9 any of the special characters: @#$%^&+=")
    if password_entered != password_re_entered: # if password entered and password reentered don't match then invalid registration
        raise ValidationError("Passwords entered don't match")

# input fields in login form
class LoginForm(FlaskForm):
    mail_id = StringField('mail_id', validators=[InputRequired(message = "Username required"), Email("This field requires a valid email address")])  #only email-id are accepted
    password = PasswordField('Password', validators=[InputRequired(message = "Password required"),invalid_credentials])


# input fields in registration form
class RegistrationForm(FlaskForm):
    mail_id = StringField('mail_id',validators=[InputRequired(message = "Mail already exists"), invalid_mail,Email("This field requires a valid email address")]) #only email-id are accepted
    password = PasswordField('password',validators=[InputRequired(message = "Password mismatch"),invalid_password])
    confirm_password = PasswordField('confirm_password')
    full_name = StringField('full_name')
    year = IntegerField('year')
    department = StringField('department')
    degree = StringField('degree')



# input fields in reset password request form
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()]) #only email-id are accepted
    submit = SubmitField('Request Password Reset')     #submit button field in the form


# input fields in reset password form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]) #confirming the password2 and checking for match using EqualTo() validator
    submit = SubmitField('Request Password Reset')    #submit button field in the form

    
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



class EventForm(FlaskForm):
    title = StringField("Title",validators=[InputRequired()])
    description = StringField("Description",validators=[InputRequired()])
    venue      = StringField("Venue",validators=[InputRequired()])
    sdate     = DateField("Start Date",format='%Y-%m-%d',validators=[InputRequired()])
    stime     = TimeField("Start Time", format="%H:%M",validators=[InputRequired()])
    edate = DateField("End Date", format='%Y-%m-%d',validators=[InputRequired()])
    etime = TimeField("End Time", format="%H:%M",validators=[InputRequired()])
    tag   = StringField("Tag",validators=[InputRequired()])
    color = SelectField("Colour",choices=[('#4fbd0a',' green'),('#082b96 ','blue'),('#4a0896 ','violet'),('#96087e ','purple'),('#960833',' pink'),('#960808 ','maroon'),('#bd5a0a','brown'),('#089669 ','navygreen'),('#086e96',' navyblue')])