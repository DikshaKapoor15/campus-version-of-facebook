from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Credentials(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(25), unique = True, nullable = False)
    password = db.Column(db.String(), nullable= False)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(25), unique = True, nullable = False)
    full_name = db.Column(db.String(), nullable= False)
    year = db.Column(db.Integer, nullable = False)
    department = db.Column(db.String(), nullable= False)
    degree = db.Column(db.String(), nullable= False)
