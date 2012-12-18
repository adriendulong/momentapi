from api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    age = db.Column(db.Integer)
    pwd = db.Column(db.String(80))

    def __init__(self, username, email, age, pwd):
        self.username = username
        self.email = email
        self.age = age
        self.pwd = pwd

    def __repr__(self):
        return '<User %r>' % self.username