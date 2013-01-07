# -*- coding: utf-8 -*-
from api import db
import datetime
import os
import variables


##########################################
######### HELPER TABLES INVITATION #######
##########################################

"""
no_reply_invitations = db.Table('no_reply_invitations',
    db.Column('moment_id', db.Integer, db.ForeignKey('moment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

moment_owners = db.Table('moment_owners',
    db.Column('moment_id', db.Integer, db.ForeignKey('moment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

coming_users = db.Table('coming_users',
    db.Column('moment_id', db.Integer, db.ForeignKey('moment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

not_coming_users = db.Table('not_coming_users',
    db.Column('moment_id', db.Integer, db.ForeignKey('moment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

maybe_users = db.Table('not_coming_users',
    db.Column('moment_id', db.Integer, db.ForeignKey('moment.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
"""


################################
##### Une invitation ###########
################################

class Invitation(db.Model):
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # 0 = Owner, 1 = Going, 2 = Maybe, 3 = Not Going
    state = db.Column(db.Integer)
    user = db.relationship("User", backref="invitations")

    def __init__(self, state, user):
        self.state = state
        self.user = user


################################
##### Un utilisateur ###########
################################

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    pwd = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    facebookId = db.Column(db.Integer)
    creationDateUser = db.Column(db.Date)
    goldProfileNumber = db.Column(db.Integer)
    secondEmail = db.Column(db.String(80))
    secondPhone = db.Column(db.String(20))
    lastConnection = db.Column(db.DateTime)
    profile_picture = db.Column(db.String(120))

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

    def __init__(self, email, firstname, lastname, pwd):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.pwd = pwd
        self.creationDateUser = datetime.date.today()


    def __repr__(self):
        return '<User %r>' % self.email


    #Fonction qui renvoit les nb_moments futurs du user 
    def get_moments(self, nb_moments):

        moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.email== self.email).limit(nb_moments).all()

        return moments


###########################################
####### Un Moment #########################
###########################################


class Moment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160))
    address = db.Column(db.Text)
    placeInformations = db.Column(db.Text)
    startDate = db.Column(db.Date)
    startTime = db.Column(db.Time)
    endDate = db.Column(db.Date)
    endTime = db.Column(db.Time)
    description = db.Column(db.Text)
    hashtag = db.Column(db.String(60))
    facebookId = db.Column(db.Integer)

    #no_reply_users = db.relationship('User', secondary=no_reply_invitations, backref='moments_no_reply')
    #coming_users = db.relationship('User', secondary=coming_users, backref='moments_replied_coming')
    #not_coming_users = db.relationship('User', secondary=not_coming_users, backref='moments_replied_not_coming')
    #maybe_users = db.relationship('User', secondary=maybe_users, backref='moments_replied_maybe')
    #owners = db.relationship('User', secondary=moment_owners, backref='moments_is_owner')

    guests = db.relationship("Invitation", backref="moment")

    def __init__(self, name, address, startDate, endDate):
        self.name = name
        self.address = address
        self.startDate = startDate
        self.endDate = endDate

    def __repr__(self):
        return '<Moment name :%r, start date :>' % (self.name)

    def moment_to_send(self):

        #On construit le Moment tel qu'on va le renvoyer à l'app
        moment = {}
        moment["name"] = self.name
        moment["address"] = self.address
        moment["startDate"] = "%s-%s-%s" %(self.startDate.year, self.startDate.month, self.startDate.day)
        moment["endDate"] = "%s-%s-%s" %(self.endDate.year, self.endDate.month, self.endDate.day)
        
        if self.description is not None:
            moment["description"] = self.description

        if self.placeInformations is not None:
            moment["placeInformations"] = self.placeInformations
        
        if self.hashtag is not None:
            moment["hashtag"] = self.hashtag

        if self.facebookId is not None:
            moment["facebookId"] = self.facebookId

        if self.startTime is not None:
            moment["startTime"] = "%s:%s:%s" %(self.startTime.hour, self.startTime.minute, self.startTime.second)

        if self.endTime is not None:
            moment["endTime"] = "%s:%s:%s" %(self.endTime.hour, self.endTime.minute, self.endTime.second)

        return moment


    def create_paths(self):
        # On créé tous les dossiers necessaires à ce Moment
        path_moment = "%s%s" % (variables.MOMENT_PATH , self.id)
        os.mkdir(path_moment)
        os.mkdir(path_moment+"/photos")
        os.mkdir(path_moment+"/cover")










