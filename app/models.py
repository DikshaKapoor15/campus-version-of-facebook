from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class Credentials(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(25), unique = True, nullable = False)
    password = db.Column(db.String(), nullable= False)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mail_id = db.Column(db.String(50), unique = True, nullable = False)
    full_name = db.Column(db.String(), nullable= False)
    year = db.Column(db.Integer, nullable = False)
    department = db.Column(db.String(), nullable= False)
    degree = db.Column(db.String(), nullable= False)
    image_file = db.Column(db.LargeBinary)   ##to be seen

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=False), nullable=False)

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

class post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail_id = db.Column(db.String(25), unique=True, nullable=False)
    date = db.Column(db.DateTime(timezone=False), nullable=False)
    post_description = db.Column(db.String(), nullable=False)
    tag1 = db.Column(db.String(), nullable=False)
    tag2 = db.Column(db.String(), nullable=True)
    tag3 = db.Column(db.String(), nullable=True)
    post_img = db.Column(db.LargeBinary, nullable=True)

    def __init__(self, mid, d, pd, t1, t2, t3, pi):
        self.mail_id = mid
        self.date = d
        self.post_description = pd
        self.tag1 = t1
        self.tag2 = t2
        self.tag3 = t3
        self.post_img = pi

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

