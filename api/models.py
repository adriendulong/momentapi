# -*- coding: utf-8 -*-
from api import db, app
import user.userConstants as userConstants
import datetime
import os
import constants
import fonctions
from PIL import Image
from gcm import GCM
import thread
import StringIO
from sqlalchemy import and_, UniqueConstraint
from aws_S3 import S3
from mail import Mail
from bcrypt import hashpw, gensalt


##########################################
######### HELPER TABLES INVITATION #######
##########################################


invitations_prospects = db.Table('invitations_prospect',
    db.Column('moment_id', db.Integer, db.ForeignKey('moment.id')),
    db.Column('prospect_id', db.Integer, db.ForeignKey('prospect.id'))
)


likes_table = db.Table('likes', 
    db.Column('photo_id', db.Integer, db.ForeignKey('photo.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

followers_table = db.Table("followers_table", 
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
)

waiting_followers_table = db.Table("waiting_followers_table", 
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
)

feed_photos = db.Table("feed_photos", 
    db.Column("feed", db.Integer, db.ForeignKey("feed.id"), primary_key=True),
    db.Column("photo", db.Integer, db.ForeignKey("photo.id"), primary_key=True)
)

feed_chats = db.Table("feed_chats", 
    db.Column("feed", db.Integer, db.ForeignKey("feed.id"), primary_key=True),
    db.Column("chat", db.Integer, db.ForeignKey("chat.id"), primary_key=True)
)

feed_follows = db.Table("feed_follows", 
    db.Column("feed", db.Integer, db.ForeignKey("feed.id"), primary_key=True),
    db.Column("user", db.Integer, db.ForeignKey("user.id"), primary_key=True)
)




################################
##### Une invitation ###########
################################

class Favoris(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    favoris_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    
    score = db.Column(db.Integer)

    def __init__(self, user):
        self.score = 0
        self.favoris_id = user.id



#############################################################################
##### Actu of a user (all the action that can  be seen by his followers) ###########
#############################################################################

class Actu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_action = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'))
    photo_id = db.Column(db.Integer, db.ForeignKey('photo.id'))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))
    follow_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime, default = datetime.datetime.now())

    def __init__(self, moment , user, type_action, id_element = None):
        self.user_id = user.id
        self.type_action = type_action
        self.time = datetime.datetime.now()

        if type_action == userConstants.ACTION_PHOTO:
            self.photo_id = id_element
            self.moment_id = moment.id

        elif type_action == userConstants.ACTION_CHAT:
            self.chat_id = id_element
            self.moment_id = moment.id

        elif type_action == userConstants.ACTION_FOLLOW:
            self.follow_id = id_element

        else:
            self.moment_id = moment.id





################################
##### Une Notification ###########
################################

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_notif = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, default = datetime.datetime.now())

    #Le user Ã  qui appartient la notif
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    #Le user qui a suivi ou qui a fait la requete de follow
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'))
    moment = db.relationship("Moment", backref=db.backref("notifications", cascade="delete, delete-orphan"))

    #Definit si la notif est en cours ou si elle est passÃ©e dans l'historique (False)
    is_active = db.Column(db.Boolean, default=True)

    


    def __init__(self, concerned, user, type_notif):
        self.type_notif = type_notif

        #Si la notif concerne un moment alors concerned sera un moment
        if self.type_notif != userConstants.NEW_FOLLOWER and self.type_notif != userConstants.NEW_REQUEST:
            self.moment = concerned

        #Sinon Ã§a sera le user qui suit ou a fait la requete pour
        else:
            self.follower = concerned

        self.user = user
        self.time = datetime.datetime.now()

    def notif_to_send(self):
        notif = {}
        notif["time"] = self.time.strftime("%s")
        if self.type_notif != userConstants.NEW_FOLLOWER and self.type_notif != userConstants.NEW_REQUEST:
            notif["moment"] = self.moment.moment_to_send(self.user_id)
        elif self.type_notif == userConstants.NEW_FOLLOWER:
            notif["follower"] = self.follower.user_to_send_social(self.user)
        else:
            notif["request_follower"] = self.follower.user_to_send_social(self.user)
        notif["type_id"] = self.type_notif

        return notif




#############################################################################
###########################    Feed d'un utilisateur   ######################
#############################################################################

class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_action = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'))
    time = db.Column(db.DateTime, default = datetime.datetime.now())

    #The photos that has been by the user followed
    photos = db.relationship("Photo",
                    secondary=feed_photos,
                    backref=db.backref("feeds", cascade="delete"),
                    cascade = "delete")

    #The chats that has been added by the user followed
    chats = db.relationship("Chat",
                    secondary=feed_chats,
                    backref=db.backref("feeds", cascade="delete"),
                    cascade = "delete")

    #The user that has been followed by the user followed
    follows = db.relationship("User",
                    secondary=feed_follows,
                    backref=db.backref("feeds_followed_concerned", cascade="delete"),
                    cascade = "delete")


    def __init__(self, time,  followed, type_action, moment_id = None):
        self.followed = followed
        self.type_action = type_action
        self.time = time

        if type_action != userConstants.ACTION_FOLLOW:
            self.moment_id = moment_id


    def feed_to_send(self):
        reponse = {}

        reponse["id"] = self.id
        reponse["user"] = self.followed.user_to_send()
        reponse["time"] = self.time.strftime("%s")
        reponse["type_action"] = self.type_action
        

        if self.type_action == userConstants.ACTION_PHOTO:
            reponse["photos"] = []
            reponse["moment"] = self.moment.moment_to_send()

            for photo in self.photos:
                 reponse["photos"].append(photo.photo_to_send_short())

            reponse["nb_photos"] = len(self.photos)

        elif self.type_action == userConstants.ACTION_CHAT:
            reponse["chats"] = []
            reponse["moment"] = self.moment.moment_to_send()
            reponse["chats"].append(self.chats[len(self.chats)-1].chat_to_send())
            reponse["nb_chats"] = len(self.chats)

        elif self.type_action == userConstants.ACTION_FOLLOW:
            reponse["follows"] = []

            for follow in self.follows:
                reponse["follows"].append(follow.user_to_send())

        else:
            reponse["moment"] = self.moment.moment_to_send_short()
            

        return reponse






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
    phoneCountry = db.Column(db.String(30))
    facebookId = db.Column(db.BigInteger)
    creationDateUser = db.Column(db.Date)
    goldProfileNumber = db.Column(db.Integer)
    secondEmail = db.Column(db.String(80))
    secondPhone = db.Column(db.String(20))
    lastConnection = db.Column(db.DateTime)
    profile_picture_url = db.Column(db.String(120))
    profile_picture_path = db.Column(db.String(120))
    lang = db.Column(db.String(40))
    last_feed_update = db.Column(db.DateTime)
    description = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    sex = db.Column(db.String(1))
    privacy = db.Column(db.Integer, default = userConstants.PRIVATE)

    #Les paramÃ¨tres de notifications
    param_notifs = db.relationship("ParamNotifs", backref="user")

    #Les favoris du user
    favoris = db.relationship("Favoris", backref='has_favoris',
                             primaryjoin=id==Favoris.user_id)

    is_favoris = db.relationship("Favoris", backref='the_favoris',
                             primaryjoin=id==Favoris.favoris_id)
    photos = db.relationship("Photo", backref="user")
    devices = db.relationship("Device", backref="user", cascade = "delete, delete-orphan")
    chats = db.relationship("Chat", backref="user")
    notifications = db.relationship("Notification", backref="user", foreign_keys=[Notification.user_id])

    #All the actus of this users
    actus = db.relationship("Actu", backref="user", foreign_keys=[Actu.user_id])

    #All the people this user follows
    follows = db.relationship("User",
                        secondary=followers_table,
                        primaryjoin=id==followers_table.c.follower_id,
                        secondaryjoin=id==followers_table.c.followed_id,
                        backref="followers"
    )


    #All the people this user asked to follow
    waitingFollows = db.relationship("User",
                        secondary=waiting_followers_table,
                        primaryjoin=id==waiting_followers_table.c.follower_id,
                        secondaryjoin=id==waiting_followers_table.c.followed_id,
                        backref="requestFollowers"
    )

    #The feeds of the user
    feeds = db.relationship("Feed", backref="user", cascade = "delete, delete-orphan", foreign_keys=[Feed.user_id])

    #Liens avec tous les feed dans lesquel ce user apparait
    concerned_feeds = db.relationship("Feed", backref="followed", cascade = "delete, delete-orphan", foreign_keys=[Feed.followed_id])

    #Liens avec toutes les actus dans lesquelles ce user est concernÃ© (parce qu'il a Ã©tÃ© suivi)
    concerned_actus = db.relationship("Actu", backref="follow", cascade = "delete, delete-orphan", foreign_keys=[Actu.follow_id])

    #liens avec toutes les noftifs dans lesquels ce user apparait
    concerned_notifs = db.relationship("Notification", backref="follower", cascade = "delete, delete-orphan", foreign_keys=[Notification.follower_id])

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
        self.last_feed_update = datetime.datetime.now()

        #On crÃ©Ã© tous les paramtres pour controller les notifs
        self.create_params_notifs()

    def __cmp__(self, other):
        if self.id < other.id:  # compare name value (should be unique)
          return -1
        elif self.id > other.id:
          return 1
        else: return 0 


    def __repr__(self):
        return '<User %r>' % self.email


    #Fonction qui renvoit les nb_moments futurs du user 
    def get_moments(self, nb_moments):

        moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.email== self.email).limit(nb_moments).all()

        return moments

    #Fonction qui va updater la denriere connection du user
    def update_last_connection(self):
        self.lastConnection = datetime.datetime.now()


    ##
    # Modify the password
    ##

    def modify_pass(self, new_pass, email):
        hashpwd = hashpw(new_pass, gensalt())
        self.pwd = hashpwd

        #On construit le tableau de destinataire
        if email:
            to_dests = []
            dest = {
                "email" : self.email,
                "name" : "%s %s" % (self.firstname, self.lastname)
            }
            to_dests.append(dest)

            #On envoie le mail
            thread.start_new_thread( fonctions.send_new_pass_mail, (to_dests, new_pass,) )


        print new_pass

        

        db.session.commit()



    #Fonction qui renvoit les nb_moments sup Ã  date
    def get_moments_sup_date(self, nb_moments, date, equal):

        if equal:
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate >= date).order_by(Moment.startDate.asc()).limit(nb_moments).all()

            #Si on a recupÃ©rÃ© des moments
            if len(moments) > 0:

                last_moment = moments[len(moments)-1]

                #Si il y en a on recupere aussi les moments de la derniere journÃ©e
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.asc()).all()

                for moment in moments_day:
                    isPresent = False
                    for moment_futur in moments:
                        if moment == moment_futur:
                            isPresent = True

                    if not isPresent:
                        moments.append(moment)

            
        else:
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate > date).order_by(Moment.startDate.asc()).limit(nb_moments).all()

            #Si on a recupÃ©rÃ© des moments
            if len(moments) > 0:

                last_moment = moments[len(moments)-1]

                #Si il y en a on recupere aussi les moments de la derniere journÃ©e
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.asc()).all()

                for moment in moments_day:
                    isPresent = False
                    for moment_futur in moments:
                        if moment == moment_futur:
                            isPresent = True

                    if not isPresent:
                        moments.append(moment)

        return moments





    #Fonction qui renvoit les nb_moments inf Ã  date
    def get_moments_inf_date(self, nb_moments, date, equal):

        if equal:
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate <= date).order_by(Moment.startDate.desc()).limit(nb_moments).all()

            #Si on a recupÃ©rÃ© des moments
            if len(moments) > 0:

                last_moment = moments[0]

                #Si il y en a on recupere aussi les moments de la derniere journÃ©e
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.desc()).all()

                for moment in moments_day:
                    isPresent = False
                    for moment_past in moments:
                        if moment == moment_past:
                            isPresent = True

                    if not isPresent:
                        moments.append(moment)


        else:
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate < date).order_by(Moment.startDate.desc()).limit(nb_moments).all()

            #Si on a recupÃ©rÃ© des moments
            if len(moments) > 0:

                last_moment = moments[0]

                #Si il y en a on recupere aussi les moments de la derniere journÃ©e
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.desc()).all()

                for moment in moments_day:
                    isPresent = False
                    for moment_past in moments:
                        if moment == moment_past:
                            isPresent = True

                    if not isPresent:
                        moments.append(moment)

        return moments


    #Fonction qui met en forme un user pour le renvoyÃ©
    def user_to_send(self):
        
        user = {}

        # Valeurs obligatoire donc toujours prÃ©sentes
        user["id"] = self.id
        user["firstname"] = self.firstname
        user["lastname"] = self.lastname
        user["email"] = self.email
        user["privacy"] = self.privacy

        if self.phone is not None:
            user["phone"] = self.phone

        if self.profile_picture_url is not None:
            user["profile_picture_url"] = self.profile_picture_url

        #Autres valeurs
        if self.facebookId is not None:
            user["facebookId"] = self.facebookId

        if self.secondEmail is not None:
            user["secondEmail"] = self.secondEmail

        if self.secondPhone is not None:
            user["secondPhone"] = self.secondPhone

        if self.description is not None:
            user["description"] = self.description

        user["nb_follows"] = len(self.follows)
        user["nb_followers"] = len(self.followers)
        user["nb_photos"] = len(self.photos)
        user["nb_moments"] = len(self.invitations)

        return user

    ####
    # Fonction qui renvoit en plus de user_to_send l'info si le user suit dÃ©jÃ  un user donnÃ©

    def user_to_send_social(self, user):

        user_to_send = self.user_to_send()
        user_to_send["is_followed"] = False
        user_to_send["request_follower"] = False
        user_to_send["request_follow_me"] = False
        user_to_send["privacy"] = self.privacy

        

        #On pourcours les gens qui suivent ce user pour voir si y en a un qui correpond au user connectÃ©
        for follow in user.follows:
            if follow.id == self.id:
                user_to_send["is_followed"] = True


        #Renvoit si ce user a demandÃ© de suivre self
        #Ca ne sert Ã  rien de regarder si ce self n'est pas en private
        if self.privacy == userConstants.PRIVATE:
            for requestFollower in self.requestFollowers:
                if requestFollower.id == user.id:
                    user_to_send["request_follower"] = True

        #Renvoit si self a demandÃ© Ã  suivre ce user
        if user.privacy==userConstants.PRIVATE:
            for waitingFollow in self.waitingFollows:
                if waitingFollow.id == user.id:
                    user_to_send["request_follow_me"] = True

                

        return user_to_send
                


        



        user["is_followed"]


    #Renvoie le chemin vers le dossiers de ce user, CrÃ©Ã© si il n'existe pas
    def get_user_dir(self):
        #On verifie que le dossier existe
        path_user = "%s/%s" % (constants.PROFILE_PATH, self.id)
        if os.path.exists(app.root_path + path_user):
            return path_user
        #Sinon on le crÃ©Ã©
        else:
            os.mkdir(app.root_path + path_user)
            return path_user


    #Fonction qui rajoute une image de profile
    def add_profile_picture(self, f, name):
        #On recupere le path du user
        user_path = self.get_user_dir()

        # On vÃ©rifie que le chemin pour enregistrer sa photo de profil existe
        if os.path.exists(app.root_path + user_path+"/profile_pictures"):
            im_original = Image.open(f)
            im_original.thumbnail(constants.SIZE_MEDIUM, Image.ANTIALIAS)
            im_original.save(app.root_path + user_path+"/profile_pictures/"+name+".jpg", "JPEG")
            return user_path+"/profile_pictures/"+name+".jpg"
        #sinon on crÃ©Ã© le chemin en question
        else:
            os.mkdir(app.root_path + user_path+"/profile_pictures")
            im_original = Image.open(f)
            im_original.thumbnail(constants.SIZE_MEDIUM, Image.ANTIALIAS)
            im_original.save(app.root_path + user_path+"/profile_pictures/"+name+".jpg", "JPEG")
            return user_path+"/profile_pictures/"+name+".jpg"

    def add_profile_picture_aws(self, f, name):

        #BUild the path which will be : data/users/9/
        path = "%s%s/" % (constants.AWS_PROFILE_PATH, self.id)
        name = "profile_picture_%s" % self.id

        #Image buffer user to temporary hold the file
        img_buff = StringIO.StringIO()

        im_original = Image.open(f)
        im_original.thumbnail(constants.SIZE_MEDIUM, Image.ANTIALIAS)
        im_original.save(img_buff, "JPEG")

        #We seek to 0 in the Image Buffer
        img_buff.seek(0)

        s3 = S3()
        #We upload the file to S3
        if s3.upload_file(path, name, "jpg", img_buff, True):
            self.profile_picture_path = path + name + ".jpg"
            self.profile_picture_url = constants.S3_URL + constants.S3_BUCKET + path + name +".jpg"
            return True

        else:
            return False


    #fonctions qui crÃ©Ã© un favoris si il n'existe pas, ou increment son score si il existe
    def increment_favoris(self, user, score):
        
        #On regarde si c'est dÃ©jÃ  un favoris
        for favoris_user in self.favoris:
            #Si on le trouve on augmente son score
            if favoris_user.favoris_id == user.id:
                favoris_user.score += score
                return True


        #Sinon on en crÃ©Ã© un nouveau 
        new_fav = Favoris(user)
        new_fav.score += score
        self.favoris.append(new_fav)

        return True


    #Fonction qui verifie que le device n'est pas dejÃ  associÃ© Ã  ce user, et le crÃ©Ã© sinon
    def add_device(self, device_id, os, os_version, model):
        for device in self.devices:
            if device.device_id == device_id:
                device.os = os
                device.os_version = os_version
                device.model = model
                return device

        #On verifie qu'il existe pas dÃ©jÃ  un device avec ce meme device_id
        sameDevice = Device.query.filter(Device.device_id == device_id).first()
        #Si il en existe un Ã§a veut dire qu'on la pas effacÃ© quand quelqu'un s'est deconnectÃ©, alors on l'efface maintenant
        if sameDevice is not None:
            db.session.delete(sameDevice)

        deviceTemp = Device(device_id, model, os, os_version)
        db.session.add(deviceTemp)
        self.devices.append(deviceTemp)
        db.session.commit()
        return deviceTemp


    #Recupere l'objet Device ayant le device_id donné

    def get_device(self, device_id):

        for device in self.devices:
            if device.device_id == device_id:
                return device



    def has_notif_id(self):
        for device in self.devices:
            if device.notif_id is not None:
                return True

        return False



    #Fonction qui update un user en fonction des champs d'un prospect
    def update_from_prospect(self, prospect):
        if self.firstname is None or self.firstname == ""  and prospect.firstname is not None:
            self.firstname = prospect.firstname

        if self.lastname is None or self.lastname == "" and prospect.lastname is not None:
            self.lastname = prospect.lastname

        if self.phone is None or self.phone == "" and prospect.phone is not None:
            self.phone = prospect.phone

        if self.email is None or self.email == "" and prospect.email is not None:
            self.email = prospect.email

        if self.facebookId is None and prospect.facebookId is not None:
            self.facebookId = prospect.facebookId

        if self.secondEmail is None or self.secondEmail == "" and prospect.secondEmail is not None:
            self.secondEmail = prospect.secondEmail

        if self.secondPhone is None or self.secondPhone == "" and prospect.secondPhone is not None:
            self.secondPhone = prospect.secondPhone

        if self.profile_picture_url is None and prospect.profile_picture_url is not None:
            self.profile_picture_url = prospect.profile_picture_url


    #####
    ## Fonction qui rajoute rajoute un user qui va etre follow
    #####

    def add_follow(self, user):

        #On verifie que le user est pas dÃ©jÃ  suivi
        for follow in self.follows:
            if follow.id == user.id:
                return False

        #Si c est pas le cas on le rajoute
        self.follows.append(user)
        db.session.commit()
        #On notifie ce user qu'il est suivie
        user.notify_new_follower(self)

        #On l'enregistre dans les actus
        self.add_actu_follow(user)
        return True


    ###
    # Fonction qui envoie un requete au user et qui met en attente la demande
    ###

    def request_follow(self, user):

        for waiting in self.waitingFollows:

            #On verifie que la demande n'est pas dÃ©jÃ  en attente
            if waiting.id == user.id:
                return False

        self.waitingFollows.append(user)
        db.session.commit()

        #On notifie d'un nouvelle requete le 'user'
        user.notify_new_request(self)


    ####
    ## Fonction qui va renvoyer si ce user est dÃ©jÃ  suivi ou pas
    ####

    def is_following(self, user):

        for follow in self.follows:
            if follow.id == user.id:
                return True

        return False


    ####
    ## Fonction qui va renvoyer si la requete de follow a dÃ©jÃ  Ã©tÃ© faites
    ####

    def is_requesting(self, user):

        for waitingFollow in self.waitingFollows:
            if waitingFollow.id == user.id:
                return True

        return False


    def validate_request(self, user):

        #On verifie que la demande avait bien Ã©tÃ© faite
        if self.is_requesting(user):
            #On supprime la requete
            self.waitingFollows.remove(user)

            #On suit le user
            self.add_follow(user)

            self.notify_follow_accepted(user)

            return True

        else:
            return False

    def refuse_request(self, user):

        #On verifie que la demande avait bien Ã©été© faite
        if self.is_requesting(user):
            #On supprime la requete
            self.waitingFollows.remove(user)
            db.session.commit()

            return True

        else:
            return False
                


    ####
    ## Fonction qui eneleve un follow
    ####

    def remove_follow(self, user):

        self.follows.remove(user)
        db.session.commit()


    ####
    ## Fonction qui va renvoyer si est suivi par ce user
    ####

    def is_followed_by(self, user):

        for follower in self.followers:
            if follower.id == user.id:
                return True

        return False


    ####
    ## Nombre de notifs non lus
    ####

    def nb_notif_unread(self):

        #Nombre de nouvelles notifs
        count = 0

        for notif in self.notifications:
            if notif.is_active:
                count += 1

        print "Nb Notifs : %s" % count

        return count


    ####
    ## Passer dans l'historique toutes les notifications non lues
    ####

    def archive_notifs(self):

        #Nombre de nouvelles notifs
        count = 0

        for notif in self.notifications:
            if notif.is_active and notif.type_notif != userConstants.INVITATION:
                count += 1

                #On archive la notif
                notif.is_active = False


        #On enregistre les modifs
        db.session.commit()

        return count


    ####
    ## Passer dans l'historique toutes les notifications non lues
    ####

    def archive_invitations(self):

        #Nombre de nouvelles notifs
        count = 0

        for notif in self.notifications:
            if notif.is_active and notif.type_notif == userConstants.INVITATION:
                count += 1

                #On archive la notif
                notif.is_active = False


        #On enregistre les modifs
        db.session.commit()

        return count




    ###
    ## Fonction qui va crÃ©er un faux moment lors de l'inscription
    ###

    def create_fake_moment(self):

        #On commence par crÃ©er le moment

        #Les valeurs par defaults
        name = constants.FAKE_MOMENT_NAME
        address = constants.FAKE_MOMENT_ADDRESS
        start_date = datetime.date.today()
        end_date = datetime.date.today() + datetime.timedelta(days=3)

        moment = Moment(name, address, start_date, end_date)

        moment.description = constants.FAKE_MOMENT_DESCRIPTION

        db.session.add(moment)
        db.session.commit()

        #Puis on y met la cover par defaut

        moment.cover_picture_url = constants.FAKE_MOMENT_COVER


        #On y ajoute des photos par defaut

        photo = Photo()
        #On enregistre en base l'objet photo
        db.session.add(photo)
        db.session.commit()
        #Puis on enregistre en disque la photo
        photo.save_photo_from_url(constants.FAKE_MOMENT_PHOTO1, constants.FAKE_MOMENT_PHOTO1, self, moment)

        #2eme photo
        photo2 = Photo()
        db.session.add(photo2)
        db.session.commit()
        photo2.save_photo_from_url(constants.FAKE_MOMENT_PHOTO2, constants.FAKE_MOMENT_PHOTO2, self, moment)

        #3eme photo
        photo3 = Photo()
        db.session.add(photo3)
        db.session.commit()
        photo3.save_photo_from_url(constants.FAKE_MOMENT_PHOTO3, constants.FAKE_MOMENT_PHOTO3, self, moment)



        #On y ajoute un chat
        chat = Chat(constants.FAKE_MOMENT_CHAT, self, moment)


        #On crÃ©Ã© l'invitation qui le lie Ã  ce Moment
        # Il est owner, donc state Ã  0
        invitation = Invitation(userConstants.OWNER, self) 

        #On ratache cette invitations aux guests du nouveau Moment
        moment.guests.append(invitation)

        db.session.commit()













    ####################################################
    ###########     NOTIFICATIONS    ########################
    ###########     NOTIFICATIONS    ########################
    ###########     NOTIFICATIONS    ########################
    ##############################################


    #Fonction qui crÃ©Ã© les paramÃ¨tres de notifications en base
    def create_params_notifs(self):

        #On crÃ©Ã© le paramÃ¨tre associÃ© aux notifs d'invitation
        param_invit = ParamNotifs(userConstants.INVITATION)
        self.param_notifs.append(param_invit)

        #On crÃ©Ã© le paramÃ¨tre associÃ© aux notifs d'invitation
        param_photo = ParamNotifs(userConstants.NEW_PHOTO)
        self.param_notifs.append(param_photo)

        #On crÃ©Ã© le paramÃ¨tre associÃ© aux notifs d'invitation
        param_chat = ParamNotifs(userConstants.NEW_CHAT)
        self.param_notifs.append(param_chat)

        #On crÃ©Ã© le paramÃ¨tre associÃ© aux notifs d'invitation
        param_modif = ParamNotifs(userConstants.MODIF)
        self.param_notifs.append(param_modif)



    #########
    ## ParamÃ¨tres de Notifications
    ###########

    ##
    # Fonction qui active ou pas (Active est un Boolean) les notifs push dy 'type'
    ##

    def set_push_notif(self, type_notif, active):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le push est activÃ©
            if param_notif.type_notif == type_notif:
                param_notif.push = active


    ##
    # Fonction qui desactive toutes les notifs push
    ##

    def desactivate_all_push_notifs(self):
        self.set_push_notif(userConstants.NEW_PHOTO, False)
        self.set_push_notif(userConstants.INVITATION, False)
        self.set_push_notif(userConstants.NEW_CHAT, False)
        self.set_push_notif(userConstants.MODIF, False)




    ##
    # Fonction qui renvoie si le user veut recevoir les notifications push pour les photos
    ##

    def is_push_photo(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le push est activÃ©
            if param_notif.type_notif == userConstants.NEW_PHOTO and param_notif.push is True:
                return True

        return False




    ##
    # Fonction qui renvoie si le user veut recevoir les notifications mail pour les photos
    ##

    def is_mail_photo(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le mail est activÃ©
            if param_notif.type_notif == userConstants.NEW_PHOTO and param_notif.mail is True:
                return True

        return False


    ##
    # Fonction qui renvoie si le user veut recevoir les notifications push pour les invit
    ##

    def is_push_invit(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le push est activÃ©
            if param_notif.type_notif == userConstants.INVITATION and param_notif.push is True:
                return True

        return False


    ##
    # Fonction qui renvoie si le user veut recevoir les notifications mail pour les invit
    ##

    def is_mail_invit(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le mail est activÃ©
            if param_notif.type_notif == userConstants.INVITATION and param_notif.mail is True:
                return True

        return False


    ##
    # Fonction qui renvoie si le user veut recevoir les notifications push pour les chat
    ##

    def is_push_chat(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le push est activÃ©
            if param_notif.type_notif == userConstants.NEW_CHAT and param_notif.push is True:
                return True

        return False


    ##
    # Fonction qui renvoie si le user veut recevoir les notifications mail pour les invit
    ##

    def is_mail_chat(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le mail est activÃ©
            if param_notif.type_notif == userConstants.NEW_CHAT and param_notif.mail is True:
                return True

        return False


    ##
    # Fonction qui renvoie si le user veut recevoir les notifications push pour les chat
    ##

    def is_push_modif(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le push est activÃ©
            if param_notif.type_notif == userConstants.MODIF and param_notif.push is True:
                return True

        return False


    ##
    # Fonction qui renvoie si le user veut recevoir les notifications mail pour les invit
    ##

    def is_mail_modif(self):

        #On parcourt les parametres de notif du user
        for param_notif in self.param_notifs:

            #Quand on trouve celle correspondant aux photos, on vÃ©rifie que le mail est activÃ©
            if param_notif.type_notif == userConstants.MODIF and param_notif.mail is True:
                return True

        return False





    ##
    # Fonctions pour envoyer une notification lors d'un nouvel Ã©vÃ¨nement
    ##

    def notify_new_moment(self, moment, user_inviting):
        #On place une notifiation en base (pour le volet)
        notification = Notification(moment, self, userConstants.INVITATION)

        #On enregistre en base
        db.session.add(notification)
        db.session.commit()

        ##
        ## PUSH NOTIF
        ##

        if self.is_push_invit():

            title = "Nouvelle invitation"
            contenu = unicode('vous invite à  participer à ','utf-8')
            message = "%s %s '%s'" % (user_inviting.firstname, contenu, moment.name)

            for device in self.devices:
                device.notify_simple(moment, userConstants.INVITATION, title, message.encode('utf-8'), self)


    ##
    # Fonctions pour envoyer une notification lors d'un nouveau chat
    ##

    def notify_new_chat(self, moment, chat):
        #On enregistre la notif en base (si pas dÃ©jÃ  n'existe pas dÃ©jÃ  pour ce moment)
        notif = Notification.query.filter(and_(Notification.moment_id == moment.id , Notification.user_id == self.id, Notification.type_notif == userConstants.NEW_CHAT, Notification.is_active == True)).first()


        if notif is None:
            notification = Notification(moment, self, userConstants.NEW_CHAT)
            #On enregistre en base
            db.session.add(notification)
            db.session.commit()

        else:
            notif.time = datetime.datetime.now()

        

        ##
        ## PUSH NOTIF
        ##

        if self.is_push_chat():

            #Boolean to know if the user has connected since the last chat
            hasConnected = False
            nb_chats = len(moment.chats)

            if nb_chats > 1:
                last_connection = self.lastConnection
                lastchatTime = moment.chats[nb_chats-2].time

                #If user has connected since the last chat, hasConencted if True
                if last_connection>lastchatTime:
                    hasConnected = True

                #If the user has connected since the last time we send a push, otherwise no because he didn't even read the last one
                if hasConnected:
                    #Titre de la notif
                    title = "Nouveau Message de %s" % (chat.user.firstname)
                    contenu = "% : %s" % (chat.user.firstname, chat.message)

                    for device in self.devices:
                        device.notify_chat(moment, userConstants.NEW_CHAT,title, contenu, chat, self)

            else:
                #Titre de la notif
                title = "Nouveau Message de %s" % (chat.user.firstname)
                contenu = "% : %s" % (chat.user.firstname, chat.message)

                for device in self.devices:
                    device.notify_chat(moment, userConstants.NEW_CHAT,title, contenu, chat, self)





    ##
    ## Notification nouvelle photo
    ##

    def notify_new_photo(self, moment, photo):
        #On enregistre la notif en base (si pas dÃ©jÃ  n'existe pas dÃ©jÃ  pour ce moment)
        notif = Notification.query.filter(and_(Notification.moment_id == moment.id , Notification.user_id == self.id, Notification.type_notif == userConstants.NEW_PHOTO, Notification.is_active == True)).first()



        if notif is None:
            notification = Notification(moment, self, userConstants.NEW_PHOTO)
            #On enregistre en base
            db.session.add(notification)
            db.session.commit()

        else:
            notif.time = datetime.datetime.now()

        

        ##
        ## PUSH NOTIF
        ##

        #On envoit la notif que si le user a activÃ© l'envoie par push de nouvelles photos
        if self.is_push_photo():

            nbPhotos = len(moment.photos)

            if(nbPhotos>1):
                #We see if the timestamp of the previous photo is sup of 2 min to the new one
                oldTime = moment.photos[nbPhotos-2].creation_datetime
                newTime = moment.photos[nbPhotos-1].creation_datetime
                delta = newTime - oldTime

                print "Delta : %s" % delta.seconds

                #Send notif only if the last photos was posted more than two minutes or if it was posted by the user
                if(delta.seconds > constants.DELAY_PUSH_PHOTO) or moment.photos[nbPhotos-2].user.id == self.id:
                    #Titre de la notif
                    title = "Nouvelle photo"
                    contenu = unicode("Nouvelle photo dans ",'utf-8')
                    message = "%s '%s'" % (contenu, moment.name)

                    for device in self.devices:
                        device.notify_simple(moment, userConstants.NEW_PHOTO,title, message.encode("utf-8"), self)

            else:
                title = "Nouvelle photo"
                contenu = unicode("Nouvelle photo dans ",'utf-8')
                message = "%s '%s'" % (contenu, moment.name)

                for device in self.devices:
                    device.notify_simple(moment, userConstants.NEW_PHOTO,title, message.encode("utf-8"), self)




        ##
        # Mail Notif
        ##



    def notify_add_photo(self, moment):
        #On envoit la notif que si le user a activÃ© l'envoie par push de nouvelles photos
        #if self.is_push_photo():

        title = "Partage tes photos !"
        contenu = unicode(userConstants.PUSH_REMEMBER_ADD_PHOTO_FR, "utf8")
        name = moment.name
        message = contenu+" '"+name+"'"

        for device in self.devices:
            device.notify_from_cron(moment, userConstants.OTHER_REQUEST,title, message, self)



    ##
    ## Notification nouveau follower
    ##

    def notify_new_follower(self, follower):

        notification = Notification(follower, self, userConstants.NEW_FOLLOWER)
        
        #On enregistre en base
        db.session.add(notification)
        db.session.commit()
        #On enregistre la notif en base (si pas dÃ©jÃ  n'existe pas dÃ©jÃ  pour ce moment)

        

        ##
        ## PUSH NOTIF
        ##

        #Titre de la notif
        title = "Nouveau Follower"
        contenu = unicode('vous suit maintenant','utf-8')
        message = "%s %s" % (follower.firstname, contenu)

        for device in self.devices:
            device.notify_new_follower(title, message, follower)



    ##
    ## Notification nouvelle request de follow
    ##

    def notify_new_request(self, follower):

        notification = Notification(follower, self, userConstants.NEW_REQUEST)
        
        #On enregistre en base
        db.session.add(notification)
        db.session.commit()

        

        ##
        ## PUSH NOTIF
        ##

        #Titre de la notif
        title = "Nouvelle Requete"
        contenu = unicode('veut vous suivre','utf-8')
        message = "%s %s" % (follower.firstname, contenu)

        for device in self.devices:
            device.notify_new_follower(title, message.encode("utf-8"), follower)


    ##
    ## Mail pour nouvelle inscription
    ##

    def notify_insciption(self):

        thread.start_new_thread( fonctions.send_inscrption_mail, (self.firstname, self.lastname, self.email,) )


    ###
    ## Notify a user has accepted our request to follow him
    ###

    def notify_follow_accepted(self, user):
        title = "Requete acceptee"
        contenu = unicode("a accepte votre demande d'abonnement !",'utf-8')
        message = "%s %s" % (user.firstname, contenu)

        for device in self.devices:
            device.notify_new_follower(title, message.encode("utf-8"), user)



    ####################################################
    ###########     ACTUS USER    ########################
    ###########     ACTUS USER      ########################
    ###########     ACTUS USER      ########################
    ##############################################

    #Actu comme quoi le user a rajoutÃ© une photo sur un moment OPEN ou PUBLIC
    def add_actu_photo(self, photo, moment):

        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            if photo.id is not None:
                actu_photo = Actu(moment, self, userConstants.ACTION_PHOTO, photo.id)
                self.actus.append(actu_photo)
                db.session.commit()


    #Actu comme quoi le user a rajoutÃ© un chat sur un moment OPEN ou PUBLIC
    def add_actu_chat(self, chat, moment):

        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            actu_chat = Actu(moment, self, userConstants.ACTION_CHAT, chat.id)
            self.actus.append(actu_chat)
            db.session.commit()


    #Actu comme quoi le user a crÃ©Ã© un moment public
    def add_actu_new_moment(self, moment):
        print "CREATION"
        #On rajoute cette actu que si le moment est public ou ouvert
        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            actu_moment = Actu(moment, self, userConstants.ACTION_CREATION_EVENT)
            self.actus.append(actu_moment)
            db.session.commit()


    #Actu comme quoi le user va Ã  un moment public ou ouvert
    def add_actu_going(self, moment):

        self.remove_going_actu(moment)

        #On rajoute cette actu que si le moment est public ou ouvert
        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            actu_moment = Actu(moment, self, userConstants.ACTION_GOING)
            self.actus.append(actu_moment)
            db.session.commit()

    def remove_going_actu(self, moment):
        #Does an actu of this type for this moment already exist
        sameActu = Actu.query.filter(and_(Actu.moment_id == moment.id, Actu.user_id == self.id, Actu.type_action == userConstants.ACTION_GOING)).first()

        #if it exists an other actu for this moment for this kind of actu, we remove it
        if sameActu is not None:
            db.session.delete(sameActu)
            db.session.commit()




    #Actu comme quoi le user a Ã©tÃ© invitÃ© Ã  un moment public ou ouvert
    def add_actu_invit(self, moment):
        #On rajoute cette actu que si le moment est public ou ouvert
        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            actu_moment = Actu(moment, self, userConstants.ACTION_INVITED)
            self.actus.append(actu_moment)
            db.session.commit()


    #Actu comme quoi le user a suivi quelqu'un
    def add_actu_follow(self, userFollowed):
        actu_follow = Actu(None, self, userConstants.ACTION_FOLLOW, userFollowed.id)
        self.actus.append(actu_follow)
        db.session.commit()

    def remove_actu_follow(self, userFollowed):
        for actu in self.actus:
            if actu.type_action == userConstants.ACTION_FOLLOW and actu.follow_id == userFollowed.id:
                self.actus.remove(actu)




    ####################################################
    ###########     FEED    ########################
    ###########     FEED    ########################
    ###########     FEED    ########################
    ##############################################


    #Fonction qui va recuperer les actus de tous les users suivis et va construire la suite du feed
    def update_feed(self):

        #On parcours l'actualitÃ© de tous les follows 
        for follow in self.follows:
            #On recupere les actus de ce user qui sont sup Ã  last_feed_update
            actus = Actu.query.filter(and_(Actu.time > self.last_feed_update, Actu.user_id == follow.id)).all()

            #On initialise un tableau de feed associÃ© Ã  ce user
            feedsFollow = []

            #On partcourt les actus
            for actu in actus:

                #Si c est une actu de photo
                if actu.type_action == userConstants.ACTION_PHOTO:

                    #Boolean pour savoir si on rajoute Ã  un feed ou en crÃ©Ã© un
                    is_exist = False

                    #On regarde si dans les feed prÃ©cÃ©dents il y a avait une actu photo pour ce mÃªme moment
                    for feedFollow in feedsFollow:

                        #Si un des feed est un feed photo du mÃªme moment, on rajoute la photo
                        if feedFollow.type_action == userConstants.ACTION_PHOTO and feedFollow.moment_id == actu.moment_id:
                            feedFollow.photos.append(actu.photo)
                            is_exist = True

                    #Si finalement aucun feed ne correspondait on en crÃ©Ã© un
                    if not is_exist:
                        feed = Feed(actu.time, actu.user, actu.type_action, actu.moment_id)
                        feed.photos.append(actu.photo)
                        db.session.add(feed)
                        #On le rajoute Ã  la liste des feed
                        feedsFollow.append(feed)


                #Si c est une actu de chat
                elif actu.type_action == userConstants.ACTION_CHAT:

                    #Boolean pour savoir si on rajoute Ã  un feed ou en crÃ©Ã© un
                    is_exist = False

                    #On regarde si dans les feed prÃ©cÃ©dents il y a avit une actu chat pour ce mÃªme moment
                    for feedFollow in feedsFollow:

                        #Si un des feed est un feed photo du mÃªme moment, on rajoute la photo
                        if feedFollow.type_action == userConstants.ACTION_CHAT and feedFollow.moment_id == actu.moment_id:
                            feedFollow.chats.append(actu.chat)
                            is_exist = True

                    #Si finalement aucun feed ne correspondait on en crÃ©Ã© un
                    if not is_exist:
                        feed = Feed(actu.time, actu.user, actu.type_action, actu.moment_id)
                        feed.chats.append(actu.chat)
                        db.session.add(feed)
                        #On le rajoute Ã  la liste des feed
                        feedsFollow.append(feed)





                elif actu.type_action == userConstants.ACTION_INVITED:
                    feed = Feed(actu.time, actu.user, actu.type_action, actu.moment_id)
                    db.session.add(feed)
                    #On le rajoute Ã  la liste des feed
                    feedsFollow.append(feed)


                elif actu.type_action == userConstants.ACTION_CREATION_EVENT:
                    feed = Feed(actu.time, actu.user, actu.type_action, actu.moment_id)
                    db.session.add(feed)
                    #On le rajoute Ã  la liste des feed
                    feedsFollow.append(feed)

                elif actu.type_action == userConstants.ACTION_GOING:
                    feed = Feed(actu.time, actu.user, actu.type_action, actu.moment_id)
                    db.session.add(feed)
                    feedsFollow.append(feed)
                
                
                #Actu de type : a suivi quelqu'un 
                elif actu.type_action == userConstants.ACTION_FOLLOW:

                    #Boolean pour savoir si on rajoute Ã  un feed ou en crÃ©Ã© un
                    is_exist = False

                    #Boolean pour  savoir si cette news de follow pour ce user a dÃ©jÃ  Ã©tÃ© mise
                    already_follow = False

                    #On regarde si dans les feed prÃ©cÃ©dents il y a avait une actu "follow"
                    for feedFollow in feedsFollow:

                        #Si un des feed est un feed follow on regarde si ce user est dÃ©jÃ  pas dedans
                        if feedFollow.type_action == userConstants.ACTION_FOLLOW:

                            #On regarde si ce user etait dÃ©jÃ  dans ce feed
                            for follow in feedFollow.follows:
                                if follow.id == actu.follow.id:
                                    already_follow = True
                                    
                            #Si c est pas le cas on le rajoute
                            if not already_follow:
                                feedFollow.follows.append(actu.follow)


                            is_exist = True


                    if not is_exist:
                        feed = Feed(actu.time, actu.user, actu.type_action)
                        feed.follows.append(actu.follow)
                        db.session.add(feed)
                        #On le rajoute Ã  la liste des feed
                        feedsFollow.append(feed)
                        
                

            #On ajoute les feeds qu'on a construit dans les feeds du user
            self.feeds.extend(feedsFollow)


        #On met Ã  jour l'heure de la derniere construction du feed
        self.last_feed_update = datetime.datetime.now()

        #On sauvegarde
        db.session.commit()

        



        







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
    facebookId = db.Column(db.BigInteger)
    isOpenInvit = db.Column(db.Boolean, default=False)
    last_modification = db.Column(db.DateTime, default = datetime.datetime.now())
    cover_picture_url = db.Column(db.String(120))
    cover_picture_path = db.Column(db.String(120))
    owner_facebookId = db.Column(db.BigInteger)
    privacy = db.Column(db.Integer)
    is_sponso = db.Column(db.Boolean, default= False, nullable = False)
    unique_code = db.Column(db.String(10))

    guests = db.relationship("Invitation", backref="moment")
    prospects = db.relationship("Prospect",
                    secondary=invitations_prospects,
                    backref="invitations")
    photos = db.relationship("Photo", backref="moment")
    chats = db.relationship("Chat", backref="moment", cascade = "delete, delete-orphan")
    actus = db.relationship("Actu", backref="moment", cascade = "delete, delete-orphan")
    feeds = db.relationship("Feed", backref="moment", cascade = "delete, delete-orphan")

    def __init__(self, name, address, startDate, endDate):
        self.name = name
        self.address = address
        self.startDate = startDate
        self.endDate = endDate
        self.privacy = constants.PRIVATE

        self.init_unique_code()

        #self.last_modification = datetime.datetime.now()

    def __repr__(self):
        return '<Moment name :%r, start date :>' % (self.name)

    def moment_to_send(self, user_id):

        #On construit le Moment tel qu'on va le renvoyer Ã  l'app
        moment = {}

        #Variable qui nous permets de savoir si on a rajoutÃ© un owner
        has_owner = False

        if self.is_in_guests(user_id):
            moment["user_state"] = self.get_user_state(user_id)
        moment["id"] = self.id
        moment["name"] = self.name
        moment["address"] = self.address
        moment["startDate"] = "%s-%s-%s" %(self.startDate.year, self.startDate.month, self.startDate.day)
        moment["endDate"] = "%s-%s-%s" %(self.endDate.year, self.endDate.month, self.endDate.day)
        moment["isOpenInvit"] = self.isOpenInvit
        moment["privacy"] = self.privacy
        if self.unique_code is not None:
            moment["unique_url"] = constants.WEBSITE + constants.UNIQUE_MOMENT_URL + self.unique_code
        
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
                has_owner = True

        #Si on a pas recupÃ©re de Owner parmis les user Moment alors c est peut etre un prospect (si le moment provient d'un evenement FB)
        if not has_owner:
            #Si on a associÃ© un facebook Id au owner alors on devrait le retrouver dans les prospect
            if self.owner_facebookId is not None:
                ownerProspect = Prospect.query.filter(Prospect.facebookId == self.owner_facebookId).first()

                #Si il y en a bien un
                if ownerProspect is not None:
                    moment["owner"] = ownerProspect.prospect_to_send()
                   

        #Si il est sponsorisÃ©
        moment["is_sponso"] = self.is_sponso


        # Les invitÃ©s
        moment["guests_number"] = len(self.guests) + len(self.prospects)
        moment["guests_coming"] = self.nb_guest_coming()
        moment["guests_not_coming"] = self.nb_guest_not_coming()


        return moment


    #On renvoit les inofs de base du moment
    def moment_to_send_short(self):
        moment = {}

        moment["id"] = self.id
        moment["name"] = self.name
        if self.cover_picture_url is not None:
            moment["cover_photo_url"] = self.cover_picture_url

        return moment

    #Moment sent when requested from the external website
    def moment_to_send_ext(self):
        moment = {}
        has_owner = False

        moment["name"] = self.name
        moment["guests_number"] = len(self.guests) + len(self.prospects)
        moment["address"] = self.address
        moment["startDate"] = "%s-%s-%s" %(self.startDate.year, self.startDate.month, self.startDate.day)
        moment["endDate"] = "%s-%s-%s" %(self.endDate.year, self.endDate.month, self.endDate.day)
        if self.description is not None:
            moment["description"] = self.description
        if self.photos is not None:
            moment["nb_photos"] = len(self.photos)
        if self.chats is not None:
            moment["nb_chats"] = len(self.chats)
        if self.cover_picture_url is not None:
            moment["cover_photo_url"] = self.cover_picture_url

        #On recupere le Owner
        for guest in self.guests:
            if guest.state == 0:
                moment["owner_name"] = "%s %s" % (guest.user.firstname, guest.user.lastname)
                moment["owner_photo_url"] = guest.user.profile_picture_url
                has_owner = True

        if not has_owner:
            #Si on a associÃ© un facebook Id au owner alors on devrait le retrouver dans les prospect
            if self.owner_facebookId is not None:
                ownerProspect = Prospect.query.filter(Prospect.facebookId == self.owner_facebookId).first()

                #Si il y en a bien un
                if ownerProspect is not None:
                    moment["owner_name"] = "%s %s" % (ownerProspect.firstname, ownerProspect.lastname)
                    moment["owner_photo_url"] = ownerProspect.profile_picture_url

        if self.unique_code is not None:
            moment["unique_url"] = constants.WEBSITE + constants.UNIQUE_MOMENT_URL + self.unique_code


        return moment



    def add_cover_photo(self, f, name):
        name = "cover"
        path_moment = "%s%s/%s" % (app.root_path, constants.MOMENT_PATH , self.id)
        path_url = "%s/%s" % (constants.MOMENT_PATH , self.id)

        #f.save(path_moment + "/cover/"+name+".png")

        im_original = Image.open(f)
        im_original.thumbnail(constants.SIZE_ORIGINAL, Image.ANTIALIAS)
        im_original.save(path_moment + "/cover/"+name+".jpg", "JPEG")

        return path_url + "/cover/"+name+".jpg"


    def add_cover_photo_aws(self, f, name):
        path_moment = "%s%s/" % (constants.AWS_MOMENT_PATH , self.id)


        #Image buffer user to temporary hold the file
        img_buff = StringIO.StringIO()

        im_original = f
        im_original.thumbnail(constants.SIZE_ORIGINAL, Image.ANTIALIAS)
        im_original.save(img_buff, "JPEG")

        #We seek to 0 in the Image Buffer
        img_buff.seek(0)

        s3 = S3()
        #We upload the file to S3
        if s3.upload_file(path_moment, name, "jpg", img_buff, True):
            self.cover_picture_path = path_moment + name + ".jpg"
            self.cover_picture_url = constants.S3_URL + constants.S3_BUCKET + path_moment + name +".jpg"
            return True

        else:
            return False


    #Remove from S3 the cover file
    def delete_cover_file(self):
        s3 = S3()
        s3.delete_file(self.cover_picture_path)


    def modify_cover_photo(self, f):

        self.delete_cover_file()

        name = "cover_%s" % datetime.datetime.now().strftime("%s")
        self.add_cover_photo_aws(f, name)




    #Fonction qui renvoit si un user fait partie des invitÃ© et donc si il peut voir ce moment
    def is_in_guests(self, user_id):

        for guest in self.guests:
            if guest.user.id == user_id:
                return True

        return False


    #Fonction qui dit si ce user peut modifier ce Moment
    def can_be_modified_by(self, user_id):

        for guest in self.guests:
            # On retrouve le user et on vÃ©rifie qu'il est owner ou admin
            if guest.user.id == user_id:
                if guest.state == userConstants.OWNER:
                    return True
                else:
                 return False

        return False


    def create_paths(self):

        path_moment = "%s%s/%s" % (app.root_path, constants.MOMENT_PATH , self.id)
        # On crÃ©Ã© tous les dossiers necessaires Ã  ce Moment
        if not os.path.exists(path_moment):
            os.mkdir(path_moment)
            os.mkdir(path_moment+"/photos")
            os.mkdir(path_moment+"/photos/original")
            os.mkdir(path_moment+"/photos/thumbnail")
            os.mkdir(path_moment+"/cover")

    def get_moment_path(self):

        path_moment = "%s%s/" % (constants.AWS_MOMENT_PATH , self.id)
        return path_moment



    # Fonction qui rajoute un user en invitÃ©
    # Renvoit True si rajoutÃ© correctement 
    # False sinon
    def add_guest(self, user_id, state):

        user = User.query.get(user_id)


        if user is not None:
            #Si il n'est pas dÃ©jÃ  invitÃ©
            if not self.is_in_guests(user.id):
                invitation = Invitation(state, user)
                self.guests.append(invitation)

                return True
            else:
                return False

        else:
            return False


    # Fonction qui rajoute un user en invitÃ© Ã  partir d'un objet user
    # Renvoit True si rajoutÃ© correctement 
    # False sinon
    def add_guest_user(self, user, user_inviting, state):

        if user is not None:
            #Si il n'est pas dÃ©jÃ  invitÃ©
            if not self.is_in_guests(user.id):
                invitation = Invitation(state, user)
                self.guests.append(invitation)

                #On le notifie (dans un thread different pour pas ralentir la requete)
                user.notify_new_moment(self, user_inviting)
                


                #ON increment egalement leur compteur favoris respectif
                if user_inviting is not None:
                    user_inviting.increment_favoris(user, userConstants.AJOUT)
                    user.increment_favoris(user_inviting, userConstants.INVITE)

                #On increment le compteur pour chaque invitÃ© egalement
                for guest in self.guests:
                    if guest.user.id != user.id and guest.user.id != user_inviting.id:
                        guest.user.increment_favoris(user, userConstants.MOMENT)

                return True
            else:
                return False

        else:
            return False


    def add_myself_to_moment(self, user):

        #On verifie que le moment est bien un moment public
        if self.privacy == constants.PUBLIC:

            if user is not None:
                #Si il n'est pas dÃ©jÃ  invitÃ©
                if not self.is_in_guests(user.id):
                    invitation = Invitation(userConstants.COMING, user)
                    self.guests.append(invitation)

                    #On increment le compteur pour chaque invitÃ© egalement
                    for guest in self.guests:
                        if guest.user.id != user.id:
                            guest.user.increment_favoris(user, userConstants.MOMENT)

                    #On rajoute dans l'actu de la personne
                    user.add_actu_going(self)

                    return True
                else:
                    return False

            else:
                return False




    #Fonction qui dit si ce user peut ajouter des invites
    def can_add_guest(self, user_id):

        if self.isOpenInvit:
            return True
        elif self.privacy == userConstants.OPEN:
            return True
        else:
            for guest in self.guests:
                # On retrouve le user et on vÃ©rifie qu'il est owner ou admin
                if guest.user.id == user_id:
                    if guest.state == userConstants.OWNER or guest.state == userConstants.ADMIN:
                        return True
                    else:
                        return False

            return False


    # Fonction qui renvoit l'Ã©tat de ce user (user_id) pour ce moment
    def get_user_state(self, user_id):

        for guest in self.guests:
            # On retrouve le user et on vÃ©rifie qu'il est owner ou admin
            if guest.user.id == user_id:
                return guest.state



    #Fonction qui vient modifier le "state" d'un user pour ce moment
    def modify_user_state(self, user, state):

        for guest in self.guests:
            if guest.user == user:
                guest.state = state
                db.session.commit()


    #Fonction qui renvoit le user qui est le owner de ce moment
    def get_owner(self):

        for guest in self.guests:
            if guest.state == userConstants.OWNER:
                return guest.user

    def is_owner(self, user):
        for guest in self.guests:
            if guest.state == userConstants.OWNER:
                if guest.user.id == user.id:
                    return True

        return False


    #Fonction qui dit si le user est dÃ©jÃ  ADMIN ou pas
    def is_admin(self, user):

        for guest in self.guests:
            if guest.user.id == user.id:
                if guest.state == userConstants.ADMIN:
                    return True

        return False


    #Nb d'invitÃ©s qui viennent au moment
    def nb_guest_coming(self):
        count = 0

        #Nombre de gens qui viennent
        for guest in self.guests:
            if guest.state == userConstants.COMING:
                count += 1

        #On rajoute le owner
        count += 1

        #On rajoute le nb d'admin
        count += self.nb_admin()

        return count


    #Nb d'invitÃ©s ne venant pas au moment
    def nb_guest_not_coming(self):
        count = 0

        for guest in self.guests:
            if guest.state == userConstants.NOT_COMING:
                count += 1

        return count


    #Nb d'admin
    def nb_admin(self):
        count = 0

        for guest in self.guests:
            if guest.state == userConstants.ADMIN:
                count += 1

        return count


    def in_prospects(self, prospect):

        for p in self.prospects:
            if p.id == prospect.id:
                return True

        return False

    #Ajout un prospect
    def add_prospect(self, prospect):

        if not self.in_prospects(prospect):
            self.prospects.append(prospect)
            return True

        else: return False

    #Fonction qui retire un prospect
    def remove_prospect(self, prospect):

        for p in self.prospects:
            if p.id == prospect.id:
                self.prospects.remove(prospect)


    #Fonction qui prend en charge de notifier tout le monde qu'il y a un nouveau message
    def notify_users_new_chat(self, chat):

        #La liste des destinataires Ã  qui on va envoyer un mail 
        to_dests = []

        for guest in self.guests:
            #On envoit pas la notif Ã  celui qui a envoyÃ© le message
            if guest.user.id != chat.user.id:
                guest.user.notify_new_chat(self, chat)

                #Si le user accepte les notifs mail pour les photos
                if guest.user.is_mail_chat():
                    #On le rajoute Ã  la liste des destinaires
                    dest = {
                        "email" : guest.user.email,
                        "name" : "%s %s" % (guest.user.firstname, guest.user.lastname)
                    }
                    to_dests.append(dest)

        #### On envoit le mail aux destinataires


    def notify_users_new_photo(self, photo):

        #La liste des destinataires Ã  qui on va envoyer un mail 
        to_dests = []

        for guest in self.guests:
            #On envoit pas la notif Ã  celui qui a envoyÃ© le message
            if guest.user.id != photo.user.id:
                guest.user.notify_new_photo(self, photo)


                #Si le user accepte les notifs mail pour les photos
                if guest.user.is_mail_photo():
                    #On le rajoute Ã  la liste des destinaires
                    dest = {
                        "email" : guest.user.email,
                        "name" : "%s %s" % (guest.user.firstname, guest.user.lastname)
                    }
                    to_dests.append(dest)


        #### On envoit le mail aux destinataires

        ##One mail for the first photo and second photo
        if len(self.photos) <= 2:
            #On met les infos de celui qui a postÃ© la photo dans un dict
            host_infos = {}
            host_infos["firstname"] = photo.user.firstname
            host_infos["lastname"] = photo.user.lastname
            host_infos["email"] = photo.user.email
            host_infos["photo"] = photo.user.profile_picture_url

            thread.start_new_thread(fonctions.send_single_photo_mail, (to_dests, self.name, host_infos, photo.url_original,) )
        ##Each 6 photos we send an email
        elif len(self.photos) % 6 == 0:
            photosArray = []
            lenPhotos = len(self.photos)

            for photo in self.photos[(lenPhotos-7):(lenPhotos-1)]:
                photos.append(photo)

            thread.start_new_thread( fonctions.send_multiple_photo_mail, (to_dests, self.name, photosArray,) )


    #Notif sent the day after an event in order to people to think about posting photo
    def notify_users_to_add_photos(self):
        nb_users = 0

        for guest in self.guests:
            #On envoit pas la notif Ã  celui qui a envoyé le message
            guest.user.notify_add_photo(self)
            nb_users += 1

        return nb_users


    #Fcontion qui selectionne Ã  quel user on va envoyer le mail d'invit
    def mail_moment_guests(self, guests, host):

        to_dests = []

        for guest in guests:

            #Ici condition par rapport au paramtres de notif
            if guest.is_mail_invit():
                dest = {
                    "email" : guest.email,
                    "name" : "%s %s" % (guest.firstname, guest.lastname)
                }
                

                to_dests.append(dest)

        #On met les infos de celui qui invite dans un dict
        host_infos = {}
        host_infos["firstname"] = host.firstname
        host_infos["lastname"] = host.lastname
        host_infos["email"] = host.email
        host_infos["photo"] = host.profile_picture_url


        thread.start_new_thread( fonctions.send_invitation_mail, (to_dests, self.name, host_infos,) )


    #Function that send the invitation to the prospects
    def mail_moment_prospects(self, prospects, host):

        to_dests = []

        for prospect in prospects:

            #Ici condition par rapport au paramtres de notif
            if prospect.email is not None:
                dest = {
                    "email" : prospect.email,
                    "name" : "%s" % (prospect.firstname)
                }


                to_dests.append(dest)

        #On met les infos de celui qui invite dans un dict
        host_infos = {}
        host_infos["firstname"] = host.firstname
        host_infos["lastname"] = host.lastname
        host_infos["email"] = host.email
        host_infos["photo"] = host.profile_picture_url

        if self.unique_code is not None:
            unique_url = constants.WEBSITE + constants.UNIQUE_MOMENT_URL + self.unique_code
        else:
            unique_url = constants.WEBSITE


        thread.start_new_thread( fonctions.send_invitation_to_prospect_mail, (to_dests, self.name, host_infos, unique_url) )


    ##
    # Fonction qui va attribuer un identifiant unique
    ##

    def init_unique_code(self):

        while True:

            uuid = fonctions.get_uuid()

            momentExist = Moment.query.filter_by(unique_code = uuid).first()

            if momentExist is None:
                self.unique_code = uuid
                break









################################
##### Un prospect ###########
################################

class Prospect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    facebookId = db.Column(db.BigInteger)
    creationDateUser = db.Column(db.Date)
    secondEmail = db.Column(db.String(80))
    secondPhone = db.Column(db.String(20))
    profile_picture_url = db.Column(db.String(120))
    unique_code = db.Column(db.String(10))


    def get_id(self):
        return unicode(self.id)

    def __init__(self):
        self.creationDateUser = datetime.date.today()

        while True:
            #On genere un id unique
            identifier = fonctions.random_identifier()

            prospect = Prospect.query.filter_by(unique_code = identifier).first()

            if prospect is None:
                self.unique_code = identifier
                break

    def prospect_to_send(self):
        prospect = {}

        if self.email is not None:
            prospect["email"] = self.email
        if self.firstname is not None:
            prospect["firstname"] = self.firstname
        if self.lastname is not None:
            prospect["lastname"] = self.lastname
        if self.phone is not None:
            prospect["phone"] = self.phone
        if self.facebookId is not None:
            prospect["facebookId"] = self.facebookId
        if self.secondEmail is not None:
            prospect["secondEmail"] = self.secondEmail
        if self.secondPhone is not None:
            prospect["secondPhone"] = self.secondPhone
        if self.profile_picture_url is not None:
            prospect["profile_picture_url"] = self.profile_picture_url

        return prospect

    def init_from_dict(self, user):

        if "email" in user:
            self.email = user["email"]

        if "facebookId" in user:
            self.facebookId = user["facebookId"]

        if "phone" in user:
            if fonctions.phone_controll(user["phone"]) is not None:
                phone = fonctions.phone_controll(user["phone"])
                self.phone = phone["number"]

        if "secondEmail" in user:
            self.secondEmail = user["secondEmail"]

        if "secondPhone" in user:
            if fonctions.phone_controll(user["secondPhone"]) is not None:
                phone = fonctions.phone_controll(user["secondPhone"])
                self.secondPhone = phone["number"]

        if "picture_profile_url" in user:
            self.profile_picture_url = user["picture_profile_url"]

        if "firstname" in user:
            self.firstname = user["firstname"]

        if "lastname" in user:
            self.lastname = user["lastname"]

        if "photo_url" in user:
            self.profile_picture_url = user["photo_url"]




    #On update les champs 
    def update(self, user):

        #Si le mail n'est pas remplie
        if self.email is None:

            #Si l'email est fourni
            if "email" in user:
                self.email = user["email"]


        #Si le secondEmail n'est pas rempli 
        if self.secondEmail is None:

            #Si le premier email n'est pas le meme que celui enregistrÃ©
            if "email" in user:
                if user["email"] != self.email:
                    self.secondEmail = user["email"]

            elif "secondEmail" in user:
                self.secondEmail = user["secondEmail"]

        #Si le facebookId n'est pas rempli
        if self.facebookId is None:

            if "facebookId" in user:
                self.facebookId = user["facebookId"]


        #Si le phone n'est pas rempli
        if self.phone is None:

            #Si le phone est fourni
            if "phone" in user:
                if fonctions.phone_controll(user["phone"]) is not None:
                    phone = fonctions.phone_controll(user["phone"])
                    self.phone = phone["number"]

         #Si le secondPhone n'est pas rempli 
        if self.secondPhone is None:

            #Si le premier email n'est pas le meme que celui enregistrÃ©
            if "phone" in user:
                if fonctions.phone_controll(user["phone"]) is not None:
                    phone = fonctions.phone_controll(user["phone"])

                    if user["phone"] != phone["number"]:
                        self.secondPhone = phone["number"]

            elif "secondPhone" in user:
                if fonctions.phone_controll(user["secondPhone"]) is not None:
                    phone = fonctions.phone_controll(user["secondPhone"])

                    self.secondPhone = phone["number"]

        if self.firstname is None:

            if "firstname" in user:
                self.firstname = user["firstname"]


        if self.lastname is None:

            if "lastname" in user:
                self.lastname = user["lastname"]

        if self.profile_picture_url is None:

            if "photo_url" in user:
                self.profile_picture_url = user["photo_url"]



    #Fonction qui match tous les moments de ce prospect :
    # - Ajoute le nouveau user Ã  ces moments (comme invitÃ©)
    # - Enleve ce prospect des prospects invitÃ© Ã  ces moments
    def match_moments(self, user):

        #On parcourt toutes les invitations
        for moment in self.invitations:

            #On ajoute le user dans les invite
            #Et on met egalement Ã  jour les favoris
            moment.add_guest_user(user, moment.get_owner(), userConstants.UNKNOWN)

            #On supprime ce Prospect des prospects
            moment.remove_prospect(self)






################################
##### Une photo ###########
################################

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path_original = db.Column(db.String(120))
    url_original = db.Column(db.String(120))
    path_thumbnail = db.Column(db.String(120))
    url_thumbnail = db.Column(db.String(120))
    creation_datetime = db.Column(db.DateTime, default = datetime.datetime.now())
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    original_width = db.Column(db.Integer)
    original_height = db.Column(db.Integer)
    likes = db.relationship("User",
                    secondary=likes_table,
                    backref="photos_liked")
    actus = db.relationship("Actu", backref="photo", cascade = "delete, delete-orphan")
    unique_code = db.Column(db.String(10))


    def save_photo(self, f, moment, user):

        name = "%s" %(self.id)

        img_buff = StringIO.StringIO()

        #Path for the original photos
        original_path = moment.get_moment_path()+"photos/original/"
        thumbnail_path = moment.get_moment_path()+"photos/thumbnail/"

        #On se connect Ã  S3
        s3 = S3()

        #####################
        ### ORIGINAL #######
        ####################

        im_original = f
        im_original.thumbnail(constants.SIZE_ORIGINAL, Image.ANTIALIAS)

        #Avant on enregistre la largeur et la hauteur de la photo
        size = im_original.size
        self.original_width = size[0]
        self.original_height = size[1]

        im_original.save(img_buff, "JPEG")

        #We seek to 0 in the Image Buffer
        img_buff.seek(0)

        #We upload the file to S3
        if s3.upload_file(original_path, name, "jpg", img_buff, True):
            self.path_original = original_path + name + ".jpg"
            self.url_original = constants.S3_URL + constants.S3_BUCKET + original_path + name +".jpg"
        else:
            return False

        moment.photos.append(self)
        user.photos.append(self)

        
        ######################
        ####### THUMBNAIL #####
        #######################
        img_buff.seek(0)

        img_buff_thum = StringIO.StringIO()

        im = Image.open(img_buff)
        im.thumbnail(constants.SIZE_THUMBNAIL, Image.ANTIALIAS)
        thumbnail_name = "%s" % (self.id)
        im.save(img_buff_thum, "JPEG")

        img_buff_thum.seek(0)

        #We upload the file to S3
        if s3.upload_file(thumbnail_path, name, "thumbnail", img_buff_thum, True):
            self.path_thumbnail = thumbnail_path + name + ".thumbnail"
            self.url_thumbnail = constants.S3_URL + constants.S3_BUCKET + thumbnail_path + name +".thumbnail"
        else:
            return False

        #On met une heure
        self.creation_datetime = datetime.datetime.now()

        #On attribue un identifiant unique
        self.init_unique_code()



        if db.session.commit():
            print "TRUE PHOTO"

        # Le Moment s'occupe de notifier tous les invitÃ©s qu'une nouvelle photo a Ã©tÃ© ajoutÃ©e
        moment.notify_users_new_photo(self)

        user.add_actu_photo(self, moment)

        return True


    def save_photo_from_url(self, url_original, url_thumb, user, moment):

        name = "%s" %(self.id)

        self.url_original = url_original
        self.url_thumbnail = url_thumb


        moment.photos.append(self)
        user.photos.append(self)

        #On met une heure
        self.creation_datetime = datetime.datetime.now()

        #On attribue un identifiant unique
        self.init_unique_code()


        db.session.commit()

        return True



    def photo_to_send(self):
        photo = {}

        photo["id"] = self.id
        photo["url_original"] = self.url_original
        photo["url_thumbnail"] = self.url_thumbnail
        if self.user is not None:
            photo["taken_by"] = self.user.user_to_send()
        else:
            instagram_user = User.query.get(18)
            photo["taken_by"] = instagram_user.user_to_send()
        photo["nb_like"] = len(self.likes)
        photo["time"] = self.creation_datetime.strftime("%s")
        photo["original_width"] = self.original_width
        photo["original_height"] = self.original_height
        if self.unique_code is not None:
            photo["unique_url"] = constants.WEBSITE + constants.UNIQUE_PHOTO_URL + self.unique_code

        return photo


    def photo_to_send_short(self):

        photo = {}

        photo["id"] = self.id
        photo["url_original"] = self.url_original
        photo["url_thumbnail"] = self.url_thumbnail
        photo["nb_like"] = len(self.likes)
        photo["time"] = self.creation_datetime.strftime("%s")
        if self.unique_code is not None:
            photo["unique_url"] = constants.WEBSITE + constants.UNIQUE_PHOTO_URL + self.unique_code

        return photo

    def photo_to_send_ext(self):

        photo = {}

        photo["url_original"] = self.url_original
        photo["nb_like"] = len(self.likes)
        photo["time"] = "%s/%s à %s:%s" % (self.creation_datetime.day, self.creation_datetime.month, self.creation_datetime.hour, self.creation_datetime.minute)
        if self.user is not None:
            photo["taken_by"] = "%s %s" % (self.user.firstname, self.user.lastname)
        photo["moment_name"] = self.moment.name
        if self.unique_code is not None:
            photo["unique_url"] = constants.WEBSITE + constants.UNIQUE_PHOTO_URL + self.unique_code


        return photo



    #Fonction qui rajoute un like du user "user"
    def like(self, user):
        #On verifie que le user a pas dÃ©jÃ  likÃ© la photo
        for like in self.likes:
            #Si il existe on l'enleve (toggle)
            if like.id == user.id:
                self.likes.remove(like)
                db.session.commit()
                return True

        self.likes.append(user)
        db.session.commit()
        return True

    def delete_photos(self):

        s3 = S3()

        s3.delete_file(self.path_original)
        s3.delete_file(self.path_thumbnail)

        '''
        if os.path.exists(self.path_original):
            os.remove(self.path_original)
        if os.path.exists(self.path_thumbnail):
            os.remove(self.path_thumbnail)
        '''

    def save_instagram_photo(self, infos):

        print "TEST"
        #self.taken_by = infos.user["full_name"]
        self.time = infos.created_time
        self.url_original = infos.images["standard_resolution"].url
        self.original_height = infos.images["standard_resolution"].height
        self.original_width = infos.images["standard_resolution"].width
        self.url_thumbnail = infos.images["low_resolution"].url


    ##
    # Fonction qui va attribuer un identifiant unique
    ##

    def init_unique_code(self):

        while True:

            uuid = fonctions.get_uuid()

            photoExist = Photo.query.filter_by(unique_code = uuid).first()

            if photoExist is None:
                self.unique_code = uuid
                break



################################
##### Un Device ###########
################################

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(200))
    notif_id = db.Column(db.Text)
    model = db.Column(db.String(100))
    os = db.Column(db.Integer)
    os_version = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, device_id, model, os, os_version):
        self.device_id = device_id
        self.model = model
        self.os = os
        self.os_version = os_version


    def notify_simple(self, moment, type_id, titre, message, user):
        #C'est un Android
        if self.os==1:
            print "ANDROID"
            thread.start_new_thread( fonctions.send_message_device, (self.notif_id, titre, message,) )
        #C'est un iPhone
        if self.os == 0:
            print "IPHONE"
            nb_notif_unread = user.nb_notif_unread()
            thread.start_new_thread(fonctions.send_ios_notif, (moment.id, type_id, self.notif_id, message, nb_notif_unread, ))


    def notify_chat(self, moment, type_id, titre, message, chat, user):
        #C'est un Android
        if self.os==1:

            thread.start_new_thread( fonctions.send_message_device, (self.notif_id, titre, message,) )
        #C'est un iPhone
        if self.os == 0:
            #On recupere le nb de notif du user
            nb_notif_unread = user.nb_notif_unread()
            thread.start_new_thread(fonctions.send_ios_notif_chat, (moment.id, type_id, self.notif_id, message, chat.id, nb_notif_unread, ))



    def notify_new_follower(self, titre, message, follower):
        #C'est un Android
        if self.os==1:

            thread.start_new_thread( fonctions.send_message_device, (self.notif_id, titre, message,) )
        #C'est un iPhone
        if self.os == 0:
            nb_notif_unread = self.user.nb_notif_unread()
            thread.start_new_thread(fonctions.send_ios_follower_notif, (self.notif_id, message, follower.id, nb_notif_unread, ))


    def notify_from_cron(self, moment, type_id, titre, message, user):
        #C'est un Android
        if self.os==1:
            print "ANDROID"
            #thread.start_new_thread( fonctions.send_message_device, (self.notif_id, titre, message,) )
        #C'est un iPhone
        if self.os == 0:
            nb_notif_unread = user.nb_notif_unread()
            fonctions.send_ios_notif(moment.id, type_id, self.notif_id, message, nb_notif_unread)


            





################################
##### Un Chat ###########
################################

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    time = db.Column(db.DateTime, default = datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'))
    actus = db.relationship("Actu", backref="chat")

    def __init__(self, message, user, moment):
        self.message = message
        self.time = datetime.datetime.now()
        user.chats.append(self)
        moment.chats.append(self)

        #On enregistre
        db.session.add(self)
        db.session.commit()

        #On notifie tous les gens invitÃ©s Ã  ce moment que quelqu'un a ecrit un message
        moment.notify_users_new_chat(self)

        #Si l'evÃ¨nement est PUBLIC ou OPEN on enregistre cette actu
        user.add_actu_chat(self, moment)
    
        


    def chat_to_send(self):
        chat = {}
        chat["message"] = self.message
        chat["time"] = self.time.strftime("%s")
        chat["user"] = self.user.user_to_send()
        chat["id"] = self.id

        return chat

    def chat_to_send_short(self):
        chat = {}
        chat["message"] = self.message
        chat["time"] = self.time.strftime("%s")
        chat["id"] = self.id

        return chat






##
# ParamÃ¨tres de notifications permettant de savoir si le user veut recevoir des notifs par mail ou push
#
##


class ParamNotifs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_notif = db.Column(db.Integer, nullable=False)
    mail = db.Column(db.Boolean, default=True)
    push = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, type_notif):
        self.type_notif = type_notif

    def params_notifs_to_send(self):
        reponse = {}
        reponse["type_notif"] = self.type_notif
        reponse["mail"] = self.mail
        reponse["push"] = self.push

        return reponse







































