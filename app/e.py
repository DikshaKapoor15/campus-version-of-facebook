from flask import render_template
from app import app
from flask_mail import Mail
from flask_mail import Message
from app.models import *

#instantiating the mail object
mail=Mail(app)

#this function is used to set up the mail parameters
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


#send_password_reset_email function relies on send_email() function
def send_password_reset_email(user):
    print("in e.py --- reset password'''")
    # a token is generated using get_reset_password_token() function defined in models.py
    token = user.get_reset_password_token()
    # send_mail function is then invoked, with recepient being retreived from the send_password_reset_email function's
    # argument passed in application.py pertaining to the specfic route
    send_email(' Reset Your Password',
               sender="developmentsoftware305@gmail.com",
               recipients=[user.mail_id],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
