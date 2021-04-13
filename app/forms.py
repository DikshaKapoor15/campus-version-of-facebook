from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, ValidationError,DataRequired, EqualTo
from app.models import *
import datetime

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
    if password_entered != password_re_entered: # if password entered and password reentered don't match then invalid registration
        raise ValidationError("Passwords entered don't match")

# input fields in login form
class LoginForm(FlaskForm):
    mail_id = StringField('mail_id', validators=[InputRequired(message = "Username required")])
    password = PasswordField('Password', validators=[InputRequired(message = "Password required"),invalid_credentials])


# input fields in registration form
class RegistrationForm(FlaskForm):
    mail_id = StringField('mail_id',validators=[InputRequired(message = "Mail already exists"), invalid_mail])
    password = PasswordField('password',validators=[InputRequired(message = "Password mismatch"),invalid_password])
    confirm_password = PasswordField('confirm_password')
    full_name = StringField('full_name')
    year = IntegerField('year')
    department = StringField('department')
    degree = StringField('degree')


# input fields in post form
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


# input fields in reset password request form
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')


# input fields in reset password form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


# input fields in search form
class HomeForm(FlaskForm):
    tag_search = StringField('tag_search')
