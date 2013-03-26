# -*- coding: cp1252 -*-
from api import db, app
import user.userConstants as userConstants
import datetime
import os
import constants
import fonctions
from PIL import Image
from gcm import GCM
import thread
from sqlalchemy import and_, UniqueConstraint


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

"""
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


    def __init__(self, followed, type_action, moment_id = None):
        self.followed = followed
        self.type_action = type_action
        self.time = datetime.datetime.now()

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
            reponse["moment"] = self.moment.moment_to_send_short()

            for photo in self.photos:
                 reponse["photos"].append(photo.photo_to_send_short())  

        elif self.type_action == userConstants.ACTION_CHAT:
            reponse["moment"] = self.moment.moment_to_send_short()
            if len(self.chats) == 1:
                reponse["chats"] = []

                for chat in self.chats:
                     reponse["chats"].append(chat.chat_to_send_short())  

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


    #Les favoris du user
    favoris = db.relationship("Favoris", backref='has_favoris',
                             primaryjoin=id==Favoris.user_id)

    is_favoris = db.relationship("Favoris", backref='the_favoris',
                             primaryjoin=id==Favoris.favoris_id)
    photos = db.relationship("Photo", backref="user")
    devices = db.relationship("Device", backref="user")
    chats = db.relationship("Chat", backref="user")
    notifications = db.relationship("Notification", backref="user")

    #All the actus of this users
    actus = db.relationship("Actu", backref="user", foreign_keys=[Actu.user_id])

    #All the people this user follows
    follows = db.relationship("User",
                        secondary=followers_table,
                        primaryjoin=id==followers_table.c.follower_id,
                        secondaryjoin=id==followers_table.c.followed_id,
                        backref="followers"
    )

    #The feeds of the user
    feeds = db.relationship("Feed", backref="user", cascade = "delete, delete-orphan", foreign_keys=[Feed.user_id])

    #Liens avec tous les feed dans lesquel ce user apparait
    concerned_feeds = db.relationship("Feed", backref="followed", cascade = "delete, delete-orphan", foreign_keys=[Feed.followed_id])

    #Liens avec toutes les actus dans lesquelles ce user est concerné (parce qu'il a été suivi)
    concerned_actus = db.relationship("Actu", backref="follow", cascade = "delete, delete-orphan", foreign_keys=[Actu.follow_id])

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




    #Fonction qui renvoit les nb_moments sup à date
    def get_moments_sup_date(self, nb_moments, date, equal):

        if equal:
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate >= date).order_by(Moment.startDate.asc()).limit(nb_moments).all()

            #Si on a recupéré des moments
            if len(moments) > 0:

                last_moment = moments[len(moments)-1]

                #Si il y en a on recupere aussi les moments de la derniere journée
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

            #Si on a recupéré des moments
            if len(moments) > 0:

                last_moment = moments[len(moments)-1]

                #Si il y en a on recupere aussi les moments de la derniere journée
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.asc()).all()

                for moment in moments_day:
                    isPresent = False
                    for moment_futur in moments:
                        if moment == moment_futur:
                            isPresent = True

                    if not isPresent:
                        moments.append(moment)

        return moments





    #Fonction qui renvoit les nb_moments inf à date
    def get_moments_inf_date(self, nb_moments, date, equal):

        if equal:
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate <= date).order_by(Moment.startDate.desc()).limit(nb_moments).all()

            #Si on a recupéré des moments
            if len(moments) > 0:

                last_moment = moments[0]

                #Si il y en a on recupere aussi les moments de la derniere journée
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

            #Si on a recupéré des moments
            if len(moments) > 0:

                last_moment = moments[0]

                #Si il y en a on recupere aussi les moments de la derniere journée
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.desc()).all()

                for moment in moments_day:
                    isPresent = False
                    for moment_past in moments:
                        if moment == moment_past:
                            isPresent = True

                    if not isPresent:
                        moments.append(moment)

        return moments


    #Fonction qui met en forme un user pour le renvoyé
    def user_to_send(self):
        
        user = {}

        # Valeurs obligatoire donc toujours présentes
        user["id"] = self.id
        user["firstname"] = self.firstname
        user["lastname"] = self.lastname
        user["email"] = self.email
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

        return user

    ####
    # Fonction qui renvoit en plus de user_to_send l'info si le user suit déjà un user donné

    def user_to_send_social(self, user):

        user_to_send = self.user_to_send()
        user_to_send["is_followed"] = False

        #On pourcours les gens qui suivent ce user pour voir si y en a un qui correpond au user connecté
        for follow in user.follows:
            if follow.id == self.id:
                user_to_send["is_followed"] = True
                

        return user_to_send
                


        



        user["is_followed"]


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
            im_original = Image.open(f)
            im_original.thumbnail(constants.SIZE_MEDIUM, Image.ANTIALIAS)
            im_original.save(app.root_path + user_path+"/profile_pictures/"+name+".jpg", "JPEG")
            return user_path+"/profile_pictures/"+name+".jpg"
        #sinon on créé le chemin en question
        else:
            os.mkdir(app.root_path + user_path+"/profile_pictures")
            im_original = Image.open(f)
            im_original.thumbnail(constants.SIZE_MEDIUM, Image.ANTIALIAS)
            im_original.save(app.root_path + user_path+"/profile_pictures/"+name+".jpg", "JPEG")
            return user_path+"/profile_pictures/"+name+".jpg"


    #fonctions qui créé un favoris si il n'existe pas, ou increment son score si il existe
    def increment_favoris(self, user, score):
        
        #On regarde si c'est déjà un favoris
        for favoris_user in self.favoris:
            #Si on le trouve on augmente son score
            if favoris_user.favoris_id == user.id:
                favoris_user.score += score
                return True


        #Sinon on en créé un nouveau 
        new_fav = Favoris(user)
        new_fav.score += score
        self.favoris.append(new_fav)

        return True


    #Fonction qui verifie que le device n'est pas dejà associé à ce user, et le créé sinon
    def add_device(self, device_id, os, os_version, model):
        for device in self.devices:
            if device.device_id == device_id:
                device.os = os
                device.os_version = os_version
                device.model = model
                return device

        #On verifie qu'il existe pas déjà un device avec ce meme device_id
        sameDevice = Device.query.filter(Device.device_id == device_id).first()
        #Si il en existe un ça veut dire qu'on la pas effacer quand quelqu'un s'est deconnecté, alors on l'efface maintenant
        if sameDevice is not None:
            db.session.delete(sameDevice)

        deviceTemp = Device(device_id, model, os, os_version)
        db.session.add(deviceTemp)
        self.devices.append(deviceTemp)
        db.session.commit()
        return deviceTemp

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

        #On verifie que le user est pas déjà suivi
        for follow in self.follows:
            if follow.id == user.id:
                return False

        #Si c est pas le cas on le rajoute
        self.follows.append(user)
        db.session.commit()

        #On l'enregistre dans les actus
        self.add_actu_follow(user)
        return True


    ####
    ## Fonction qui va renvoyer si ce user est déjà suivi ou pas
    ####

    def is_following(self, user):

        for follow in self.follows:
            if follow.id == user.id:
                return True

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

        return len(self.notifications)









    ####################################################
    ###########     NOTIFICATIONS    ########################
    ###########     NOTIFICATIONS    ########################
    ###########     NOTIFICATIONS    ########################
    ##############################################

    def notify_new_moment(self, moment):
        #On place une notifiation en base (pour le volet)
        notification = Notification(moment, self, userConstants.INVITATION)

        #On enregistre en base
        db.session.add(notification)
        db.session.commit()

        ##
        ## PUSH NOTIF
        ##

        title = "Nouvelle invitation"
        contenu = unicode('vous invite à participer à','utf-8')
        message = "%s %s '%s'" % (moment.get_owner().firstname, contenu, moment.name)

        for device in self.devices:
            device.notify_simple(moment, userConstants.INVITATION, title, message.encode('utf-8'), self)

    def notify_new_chat(self, moment, chat):
        #On enregistre la notif en base (si pas déjà n'existe pas déjà pour ce moment)
        notif = Notification.query.filter(and_(Notification.moment_id == moment.id , Notification.user_id == self.id, Notification.type_notif == userConstants.NEW_CHAT)).first()

        if notif is None:
            notification = Notification(moment, self, userConstants.NEW_CHAT)
            #On enregistre en base
            db.session.add(notification)
            db.session.commit()

        

        ##
        ## PUSH NOTIF
        ##

        #Titre de la notif
        title = "Nouveau Message de %s" % (chat.user.firstname)

        for device in self.devices:
            device.notify_chat(moment, userConstants.NEW_CHAT,title, chat.message.encode('utf-8'), chat, self)





    ##
    ## Notification nouvelle photo
    ##

    def notify_new_photo(self, moment, photo):
        #On enregistre la notif en base (si pas déjà n'existe pas déjà pour ce moment)
        notif = Notification.query.filter(and_(Notification.moment_id == moment.id , Notification.user_id == self.id, Notification.type_notif == userConstants.NEW_PHOTO)).first()

        if notif is None:
            notification = Notification(moment, self, userConstants.NEW_PHOTO)
            #On enregistre en base
            db.session.add(notification)
            db.session.commit()

        

        ##
        ## PUSH NOTIF
        ##

        #Titre de la notif
        title = "Nouvelle photo"
        contenu = unicode('Nouvelle photo ajoutée à','utf-8')
        message = "%s '%s'" % (contenu, moment.name)

        for device in self.devices:
            device.notify_simple(moment, userConstants.NEW_PHOTO,title, message.encode("utf-8"), self)



    ####################################################
    ###########     ACTUS USER    ########################
    ###########     ACTUS USER      ########################
    ###########     ACTUS USER      ########################
    ##############################################

    #Actu comme quoi le user a rajouté une photo sur un moment OPEN ou PUBLIC
    def add_actu_photo(self, photo, moment):

        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            if photo.id is not None:
                actu_photo = Actu(moment, self, userConstants.ACTION_PHOTO, photo.id)
                self.actus.append(actu_photo)
                db.session.commit()


    #Actu comme quoi le user a rajouté un chat sur un moment OPEN ou PUBLIC
    def add_actu_chat(self, chat, moment):

        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            actu_chat = Actu(moment, self, userConstants.ACTION_CHAT, chat.id)
            self.actus.append(actu_chat)
            db.session.commit()


    #Actu comme quoi le user a créé un moment public
    def add_actu_new_moment(self, moment):

        #On rajoute cette actu que si le moment est public ou ouvert
        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            actu_moment = Actu(moment, self, userConstants.ACTION_CREATION_EVENT)
            self.actus.append(actu_moment)


    #Actu comme quoi le user va à un moment public ou ouvert
    def add_actu_going(self, moment):

        #On rajoute cette actu que si le moment est public ou ouvert
        if moment.privacy == constants.PUBLIC or moment.privacy == constants.OPEN:
            actu_moment = Actu(moment, self, userConstants.ACTION_GOING)
            self.actus.append(actu_moment)
            db.session.commit()


    #Actu comme quoi le user a été invité à un moment public ou ouvert
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

        #On parcours l'actualité de tous les follows 
        for follow in self.follows:
            #On recupere les actus de ce user qui sont sup à last_feed_update
            actus = Actu.query.filter(and_(Actu.time > self.last_feed_update, Actu.user_id == follow.id)).all()

            #On initialise un tableau de feed associé à ce user
            feedsFollow = []

            #On partcourt les actus
            for actu in actus:

                #Si c est une actu de photo
                if actu.type_action == userConstants.ACTION_PHOTO:

                    #Boolean pour savoir si on rajoute à un feed ou en créé un
                    is_exist = False

                    #On regarde si dans les feed précédents il y a avait une actu photo pour ce même moment
                    for feedFollow in feedsFollow:

                        #Si un des feed est un feed photo du même moment, on rajoute la photo
                        if feedFollow.type_action == userConstants.ACTION_PHOTO and feedFollow.moment_id == actu.moment_id:
                            feedFollow.photos.append(actu.photo)
                            is_exist = True

                    #Si finalement aucun feed ne correspondait on en créé un
                    if not is_exist:
                        feed = Feed(actu.user, actu.type_action, actu.moment_id)
                        feed.photos.append(actu.photo)
                        db.session.add(feed)
                        #On le rajoute à la liste des feed
                        feedsFollow.append(feed)


                #Si c est une actu de chat
                elif actu.type_action == userConstants.ACTION_CHAT:

                    #Boolean pour savoir si on rajoute à un feed ou en créé un
                    is_exist = False

                    #On regarde si dans les feed précédents il y a avit une actu chat pour ce même moment
                    for feedFollow in feedsFollow:

                        #Si un des feed est un feed photo du même moment, on rajoute la photo
                        if feedFollow.type_action == userConstants.ACTION_CHAT and feedFollow.moment_id == actu.moment_id:
                            feedFollow.chats.append(actu.chat)
                            is_exist = True

                    #Si finalement aucun feed ne correspondait on en créé un
                    if not is_exist:
                        feed = Feed(actu.user, actu.type_action, actu.moment_id)
                        feed.chats.append(actu.chat)
                        db.session.add(feed)
                        #On le rajoute à la liste des feed
                        feedsFollow.append(feed)





                elif actu.type_action == userConstants.ACTION_INVITED:
                    feed = Feed(actu.user, actu.type_action, actu.moment_id)
                    db.session.add(feed)
                    #On le rajoute à la liste des feed
                    feedsFollow.append(feed)


                elif actu.type_action == userConstants.ACTION_CREATION_EVENT:
                    feed = Feed(actu.user, actu.type_action, actu.moment_id)
                    db.session.add(feed)
                    #On le rajoute à la liste des feed
                    feedsFollow.append(feed)

                
                #Actu de type : a suivi quelqu'un 
                elif actu.type_action == userConstants.ACTION_FOLLOW:

                    #Boolean pour savoir si on rajoute à un feed ou en créé un
                    is_exist = False

                    #On regarde si dans les feed précédents il y a avit une actu chat pour ce même moment
                    for feedFollow in feedsFollow:

                        #Si un des feed est un feed follow on rajoute la photo
                        if feedFollow.type_action == userConstants.ACTION_FOLLOW:
                            feedFollow.follows.append(actu.follow)
                            is_exist = True


                    if not is_exist:
                        feed = Feed(actu.user, actu.type_action)
                        feed.follows.append(actu.follow)
                        db.session.add(feed)
                        #On le rajoute à la liste des feed
                        feedsFollow.append(feed)
                    


            #On ajoute les feeds qu'on a construit dans les feeds du user
            self.feeds.extend(feedsFollow)


        #On met à jour l'heure de la derniere construction du feed
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
        self.privacy = constants.PUBLIC

        #self.last_modification = datetime.datetime.now()

    def __repr__(self):
        return '<Moment name :%r, start date :>' % (self.name)

    def moment_to_send(self, user_id):

        #On construit le Moment tel qu'on va le renvoyer à l'app
        moment = {}

        #Variable qui nous permets de savoir si on a rajouté un owner
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

        #Si on a pas recupére de Owner parmis les user Moment alors c est peut etre un prospect (si le moment provient d'un evenement FB)
        if not has_owner:
            #Si on a associé un facebook Id au owner alors on devrait le retrouver dans les prospect
            if self.owner_facebookId is not None:
                ownerProspect = Prospect.query.filter(Prospect.facebookId == self.owner_facebookId).first()

                #Si il y en a bien un
                if ownerProspect is not None:
                    moment["owner"] = ownerProspect.prospect_to_send()
                   

        #Si il est sponsorisé
        moment["is_sponso"] = self.is_sponso


        # Les invités
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



    def add_cover_photo(self, f, name):
        name = "cover"
        path_moment = "%s%s/%s" % (app.root_path, constants.MOMENT_PATH , self.id)
        path_url = "%s/%s" % (constants.MOMENT_PATH , self.id)

        #f.save(path_moment + "/cover/"+name+".png")

        im_original = Image.open(f)
        im_original.thumbnail(constants.SIZE_ORIGINAL, Image.ANTIALIAS)
        im_original.save(path_moment + "/cover/"+name+".jpg", "JPEG")

        return path_url + "/cover/"+name+".jpg"




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
            os.mkdir(path_moment+"/photos/original")
            os.mkdir(path_moment+"/photos/thumbnail")
            os.mkdir(path_moment+"/cover")

    def get_moment_path(self):

        path_moment = "%s/%s" % (constants.MOMENT_PATH , self.id)
        return path_moment



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


    # Fonction qui rajoute un user en invité à partir d'un objet user
    # Renvoit True si rajouté correctement 
    # False sinon
    def add_guest_user(self, user, user_inviting, state):

        if user is not None:
            #Si il n'est pas déjà invité
            if not self.is_in_guests(user.id):
                invitation = Invitation(state, user)
                self.guests.append(invitation)

                #On le notifie (dans un thread different pour pas ralentir la requete)
                user.notify_new_moment(self)
                


                #ON increment egalement leur compteur favoris respectif
                if user_inviting is not None:
                    user_inviting.increment_favoris(user, userConstants.AJOUT)
                    user.increment_favoris(user_inviting, userConstants.INVITE)

                #On increment le compteur pour chaque invité egalement
                for guest in self.guests:
                    if guest.user.id != user.id and guest.user.id != user_inviting.id:
                        guest.user.increment_favoris(user, userConstants.MOMENT)

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

    def is_owner(self, user):
        for guest in self.guests:
            if guest.state == userConstants.OWNER:
                if guest.user.id == user.id:
                    return True

        return False


    #Fonction qui dit si le user est déjà ADMIN ou pas
    def is_admin(self, user):

        for guest in self.guests:
            if guest.user.id == user.id:
                if guest.state == userConstants.ADMIN:
                    return True

        return False


    #Nb d'invités qui viennent au moment
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


    #Nb d'invités ne venant pas au moment
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
        for guest in self.guests:
            #On envoit pas la notif à celui qui a envoyé le message
            if guest.user.id != chat.user.id:
                guest.user.notify_new_chat(self, chat)


    def notify_users_new_photo(self, photo):
        for guest in self.guests:
            #On envoit pas la notif à celui qui a envoyé le message
            if guest.user.id != photo.user.id:
                guest.user.notify_new_photo(self, photo)








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
            self.phone = user["phone"]

        if "secondEmail" in user:
            self.secondEmail = user["secondEmail"]

        if "secondPhone" in user:
            self.secondPhone = user["secondPhone"]

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

            #Si le premier email n'est pas le meme que celui enregistré
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
                self.phone = user["phone"]

         #Si le secondPhone n'est pas rempli 
        if self.secondPhone is None:

            #Si le premier email n'est pas le meme que celui enregistré
            if "phone" in user:
                if user["phone"] != self.phone:
                    self.secondPhone = user["phone"]

            elif "secondPhone" in user:
                self.secondPhone = user["secondPhone"]

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
    # - Ajoute le nouveau user à ces moments (comme invité)
    # - Enleve ce prospect des prospects invité à ces moments
    def match_moments(self, user):

        #On parcourt toutes les invitations
        for moment in self.invitations:

            #On ajoute le user dans les invite
            #Et on met egalement à jour les favoris
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
    likes = db.relationship("User",
                    secondary=likes_table,
                    backref="photos_liked")
    actus = db.relationship("Actu", backref="photo", cascade = "delete, delete-orphan")
        

    def save_photo(self, f, moment, user):

        photo_name = "%s.jpg" %(self.id)

        im_original = Image.open(f)
        im_original.thumbnail(constants.SIZE_ORIGINAL, Image.ANTIALIAS)
        im_original.save(app.root_path+moment.get_moment_path()+"/photos/original/"+photo_name, "JPEG")

        #On enregistre la photo
        #f.save(app.root_path+moment.get_moment_path()+"/photos/original/"+photo_name)

        self.path_original = app.root_path+moment.get_moment_path()+"/photos/original/"+photo_name
        self.url_original = "http://%s%s" % (app.config.get("SERVER_NAME"), moment.get_moment_path()+"/photos/original/"+photo_name)

        moment.photos.append(self)
        user.photos.append(self)

        #On créé le thumbnail
        im = Image.open(self.path_original)
        im.thumbnail(constants.SIZE_THUMBNAIL, Image.ANTIALIAS)
        thumbnail_name = "%s.thumbnail" % (self.id)
        im.save(app.root_path+moment.get_moment_path()+"/photos/thumbnail/"+photo_name, "JPEG")

        self.path_thumbnail = app.root_path+moment.get_moment_path()+"/photos/thumbnail/"+photo_name
        self.url_thumbnail = "http://%s%s" % (app.config.get("SERVER_NAME"), moment.get_moment_path()+"/photos/thumbnail/"+photo_name)

        #On met une heure
        self.creation_datetime = datetime.datetime.now()



        if db.session.commit():
            print "TRUE PHOTO"

        # Le Moment s'occupe de notifier tous les invités qu'une nouvelle photo a été ajoutée
        moment.notify_users_new_photo(self)

        user.add_actu_photo(self, moment)


    def photo_to_send(self):
        photo = {}

        photo["id"] = self.id
        photo["url_original"] = self.url_original
        photo["url_thumbnail"] = self.url_thumbnail
        photo["taken_by"] = self.user.user_to_send()
        photo["nb_like"] = len(self.likes)
        photo["time"] = self.creation_datetime.strftime("%s")

        return photo


    def photo_to_send_short(self):

        photo = {}

        photo["id"] = self.id
        photo["url_original"] = self.url_original
        photo["url_thumbnail"] = self.url_thumbnail
        photo["nb_like"] = len(self.likes)
        photo["time"] = self.creation_datetime.strftime("%s")

        return photo



    #Fonction qui rajoute un like du user "user"
    def like(self, user):
        #On verifie que le user a pas déjà liké la photo
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

        if os.path.exists(self.path_original):
            os.remove(self.path_original)
        if os.path.exists(self.path_thumbnail):
            os.remove(self.path_thumbnail)




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

            thread.start_new_thread( fonctions.send_message_device, (self.notif_id, titre, message,) )
        #C'est un iPhone
        if self.os == 0:
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

        #On notifie tous les gens invités à ce moment que quelqu'un a ecrit un message
        moment.notify_users_new_chat(self)

        #Si l'evènement est PUBLIC ou OPEN on enregistre cette actu
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




################################
##### Une Notification ###########
################################

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_notif = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, default = datetime.datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    moment_id = db.Column(db.Integer, db.ForeignKey('moment.id'), nullable=False)
    moment = db.relationship("Moment", backref=db.backref("notifications", cascade="delete, delete-orphan"))
    __table_args__ = (UniqueConstraint('moment_id', 'user_id', 'type_notif', name='_type_moment_user_uc'),
                     )

    def __init__(self, moment, user, type_notif):
        self.type_notif = type_notif
        self.moment = moment
        self.user = user

    def notif_to_send(self):
        notif = {}
        notif["time"] = self.time.strftime("%s")
        notif["moment"] = self.moment.moment_to_send(self.user_id)
        notif["type_id"] = self.type_notif

        return notif








































