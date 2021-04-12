from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from time import time
import json
import jwt
from app import app

db = SQLAlchemy()

class Credentials(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(), nullable= False)

    def get_reset_password_token(self, expires_in=6000):
        return jwt.encode(
            {'reset_password': self.mail_id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        print("heyymodels",id)
        return id


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(50), unique = True, nullable = False)
    full_name = db.Column(db.String(), nullable= False)
    year = db.Column(db.Integer, nullable = False)
    department = db.Column(db.String(), nullable= False)
    degree = db.Column(db.String(), nullable= False)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(25), nullable = False)
    date = db.Column(db.DateTime(timezone=False), nullable=False)
    post_description =db.Column(db.String(), nullable = False)
    tag1 = db.Column(db.String(), nullable = False)
    tag2 = db.Column(db.String())
    tag3 = db.Column(db.String())