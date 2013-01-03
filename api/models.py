from api import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    age = db.Column(db.Integer)
    pwd = db.Column(db.String(80))

    # Auth token for Flask Login
    def get_auth_token(self):
        """
        Encode a secure token for cookie
        """
        data = [str(self.email), self.password]
        return login_serializer.dumps(data)


    # Fonction necessary for Flask Login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __init__(self, username, email, age, pwd):
        self.username = username
        self.email = email
        self.age = age
        self.pwd = pwd

    def __repr__(self):
        return '<User %r>' % self.username