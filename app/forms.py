from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, ValidationError
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


class LoginForm(FlaskForm):
    mail_id = StringField('mail_id', validators=[InputRequired(message = "Username required")])
    password = PasswordField('Password', validators=[InputRequired(message = "Password required"),invalid_credentials])
    submit_button = SubmitField('Login')

class RegistrationForm(FlaskForm):
    mail_id = StringField('mail_id')
    password = PasswordField('password')
    confirm_password = PasswordField('confirm_password')
    full_name = StringField('full_name')
    year = IntegerField('year')
    department = StringField('department')
    degree = StringField('degree')
    submit_button = SubmitField('Register')

    def validate_mailid(self,mail_id):
        user_object = Credentials.query.filter_by(mail_id = mail_id).first()
        if user_object:
            raise ValidationError("Mailid already exists.")
