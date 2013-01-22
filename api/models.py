# -*- coding: utf-8 -*-
from api import db, app
import user.userConstants as userConstants
import datetime
import os
import constants


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
    profile_picture_url = db.Column(db.String(120))
    profile_picture_path = db.Column(db.String(120))

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


    #Fonction qui met en forme un user pour le renvoyé
    def user_to_send(self):
        
        user = {}

        # Valeurs obligatoire donc toujours présentes
        user["id"] = self.id
        user["firstname"] = self.firstname
        user["lastname"] = self.lastname
        user["email"] = self.email
        user["profile_picture_url"] = self.profile_picture_path

        #Autres valeurs

        user["facebookId"] = self.facebookId

        return user


    #Renvoie le chemin vers le dossiers de ce user, Créé si il n'existe pas
    def get_user_dir(self):
        #On verifie que le dossier existe
        path_user = "%s/%s" % (constants.PROFILE_PATH, self.id)
        if os.path.exists(app.root_path + path_user):
            return path_user
        #Sinon on le créé
        else:
            os.mkdir(app.root_path + path_user)
            return path_user


    #Fonction qui rajoute une image de profile
    def add_profile_picture(self, f, name):
        #On recupere le path du user
        user_path = self.get_user_dir()

        # On vérifie que le chemin pour enregistrer sa photo de profil existe
        if os.path.exists(app.root_path + user_path+"/profile_pictures"):
            f.save(app.root_path + user_path+"/profile_pictures/"+name+".png")
            return user_path+"/profile_pictures/"+name+".png"
        #sinon on créé le chemin en question
        else:
            os.mkdir(app.root_path + user_path+"/profile_pictures")
            f.save(app.root_path + user_path+"/profile_pictures/"+name+".png")
            return user_path+"/profile_pictures/"+name+".png"















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
    isOpenInvit = db.Column(db.Boolean, default=False)
    last_modification = db.Column(db.DateTime, default = datetime.datetime.now())
    cover_picture_url = db.Column(db.String(120))
    cover_picture_path = db.Column(db.String(120))

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

        #self.last_modification = datetime.datetime.now()

    def __repr__(self):
        return '<Moment name :%r, start date :>' % (self.name)

    def moment_to_send(self, user_id):

        #On construit le Moment tel qu'on va le renvoyer à l'app
        moment = {}
        moment["user_state"] = self.get_user_state(user_id)
        moment["id"] = self.id
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

        if self.cover_picture_url is not None:
            moment["cover_photo_url"] = self.cover_picture_url


        #On recupere le Owner
        for guest in self.guests:
            if guest.state == 0:
                moment["owner"] = guest.user.user_to_send()


        return moment


    def add_cover_photo(self, f, name):
        path_moment = "%s%s/%s" % (app.root_path, constants.MOMENT_PATH , self.id)

        f.save(path_moment + "/cover/"+name+".png")

        return path_moment + "/cover/"+name+".png"




    #Fonction qui renvoit si un user fait partie des invité et donc si il peut voir ce moment
    def is_in_guests(self, user_id):

        for guest in self.guests:
            if guest.user.id == user_id:
                return True

        return False


    #Fonction qui dit si ce user peut modifier ce Moment
    def can_be_modified_by(self, user_id):

        for guest in self.guests:
            # On retrouve le user et on vérifie qu'il est owner ou admin
            if guest.user.id == user_id:
                if guest.state == userConstants.OWNER:
                    return True
                else:
                 return False

        return False


    def create_paths(self):

        path_moment = "%s%s/%s" % (app.root_path, constants.MOMENT_PATH , self.id)
        # On créé tous les dossiers necessaires à ce Moment
        if not os.path.exists(path_moment):
            os.mkdir(path_moment)
            os.mkdir(path_moment+"/photos")
            os.mkdir(path_moment+"/cover")



    # Fonction qui rajoute un user en invité
    # Renvoit True si rajouté correctement 
    # False sinon
    def add_guest(self, user_id, state):

        user = User.query.get(user_id)

        if user is not None:
            #Si il n'est pas déjà invité
            if not self.is_in_guests(user.id):
                invitation = Invitation(state, user)
                self.guests.append(invitation)

                return True
            else:
                return False

        else:
            return False


    #Fonction qui dit si ce user peut ajouter des invites
    def can_add_guest(self, user_id):

        if self.isOpenInvit:
            return True

        else:
            for guest in self.guests:
                # On retrouve le user et on vérifie qu'il est owner ou admin
                if guest.user.id == user_id:
                    if guest.state == userConstants.OWNER or guest.state == userConstants.ADMIN:
                        return True
                    else:
                        return False

            return False


    # Fonction qui renvoit l'état de ce user (user_id) pour ce moment
    def get_user_state(self, user_id):

        for guest in self.guests:
            # On retrouve le user et on vérifie qu'il est owner ou admin
            if guest.user.id == user_id:
                return guest.state



    #Fonction qui vient modifier le "state" d'un user pour ce moment
    def modify_user_state(self, user, state):

        for guest in self.guests:
            # On retrouve le user et on vérifie qu'il est owner ou admin
            if guest.user == user:
                guest.state = state
                db.session.commit()


    #Fonction qui renvoit le user qui est le owner de ce moment
    def get_owner(self):

        for guest in self.guests:
            if guest.state == userConstants.OWNER:
                return guest.user











