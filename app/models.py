from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from time import time
from datetime import date
import json
import jwt
from app import app

db = SQLAlchemy()

# attributes in the credentials table
class Credentials(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(), nullable= False)

    #get_reset_password_token() function returns a jwt token as a string which is generated directly by jwt.encode()
    def get_reset_password_token(self, expires_in=6000):
        return jwt.encode(
            {'reset_password': self.mail_id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    #verify_reset_password_token() is a static method(can be invoked directly from class)
    #this method takes token and attempts to decode it by pyJWT's jwt.decode()
    #if the token is invalid , an exception will be raised, and in that case i catch it to prevent the error, and
    #return none to the caller

    ##if the token is valid, id is returned from the token's payload by decdding it
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return

        return id

# attributes in the profile table
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(50), unique = True, nullable = False)
    full_name = db.Column(db.String(), nullable= False)
    year = db.Column(db.Integer, nullable = False)
    department = db.Column(db.String(), nullable= False)
    degree = db.Column(db.String(), nullable= False)

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=False), nullable=False)

# attributes in the posts table
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(25), nullable = False)
    date = db.Column(db.DateTime(timezone=False), nullable=False)
    post_description =db.Column(db.String(), nullable = False)
    tag1 = db.Column(db.String(), nullable = False)
    tag2 = db.Column(db.String())
    tag3 = db.Column(db.String())

class Postss(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail_id = db.Column(db.String(25), unique=True, nullable=False)
    date = db.Column(db.DateTime(timezone=False), nullable=False)
    post_description = db.Column(db.String(),nullable=False)
    tag1  = db.Column(db.String(),nullable=False)
    tag2 = db.Column(db.String(),nullable=True)
    tag3 = db.Column(db.String(),nullable=True)
    post_img = db.Column(db.LargeBinary, nullable=False)

    def __init__(self,mid,d,pd,t1,t2,t3,pi):
        self.mail_id=mid
        self.date = d
        self.post_description =pd
        self.tag1 =t1
        self.tag2 = t2
        self.tag3 =t3
        self.post_img = pi
        #print(pd,t1,t2,t3,sep=" ")

class events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    venue = db.Column(db.String(), nullable=False)
    tag = db.Column(db.String(), nullable=False)
    sdate = db.Column(db.DateTime(timezone=False),nullable=False)
    stime = db.Column(db.DateTime(),nullable=False)
    edate = db.Column(db.DateTime(timezone=False))
    etime = db.Column(db.DateTime())

    def __init__(self,un,t,d,v,tag,sd,st,ed,et):
        self.username=un
        self.title=t
        self.description=d
        self.venue=v
        self.tag=tag
        self.sdate=sd
        self.stime=st
        self.edate=ed
        self.etime=et


class eventags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(), nullable=False)
    count = db.Column(db.Integer,nullable=False)

    def __init__(self,t,c):
        self.tag=t
        self.count=c