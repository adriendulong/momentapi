# -*- coding: utf-8 -*-
from api import db, app
import user.userConstants as userConstants
import datetime
import os
import constants
import fonctions
from PIL import Image


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

    #Les favoris du user
    favoris = db.relationship("Favoris", backref='has_favoris',
                             primaryjoin=id==Favoris.user_id)

    is_favoris = db.relationship("Favoris", backref='the_favoris',
                             primaryjoin=id==Favoris.favoris_id)
    photos = db.relationship("Photo", backref="user")

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
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate <= date).order_by(Moment.startDate.asc()).limit(nb_moments).all()

            #Si on a recupéré des moments
            if len(moments) > 0:

                last_moment = moments[0]

                #Si il y en a on recupere aussi les moments de la derniere journée
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.asc()).all()

                for moment in moments_day:
                    isPresent = False
                    for moment_past in moments:
                        if moment == moment_past:
                            isPresent = True

                    if not isPresent:
                        moments.append(moment)


        else:
            moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate < date).order_by(Moment.startDate.asc()).limit(nb_moments).all()

            #Si on a recupéré des moments
            if len(moments) > 0:

                last_moment = moments[0]

                #Si il y en a on recupere aussi les moments de la derniere journée
                moments_day = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.id== self.id).filter(Moment.startDate == last_moment.startDate).order_by(Moment.startDate.asc()).all()

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
    facebookId = db.Column(db.Integer)
    isOpenInvit = db.Column(db.Boolean, default=False)
    last_modification = db.Column(db.DateTime, default = datetime.datetime.now())
    cover_picture_url = db.Column(db.String(120))
    cover_picture_path = db.Column(db.String(120))

    guests = db.relationship("Invitation", backref="moment")
    prospects = db.relationship("Prospect",
                    secondary=invitations_prospects,
                    backref="invitations")
    photos = db.relationship("Photo", backref="moment")

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

        # Les invités
        moment["guests_number"] = len(self.guests) + len(self.prospects)
        moment["guests_coming"] = self.nb_guest_coming()
        moment["guests_not_coming"] = self.nb_guest_not_coming()


        return moment


    def add_cover_photo(self, f, name):
        path_moment = "%s%s/%s" % (app.root_path, constants.MOMENT_PATH , self.id)
        path_url = "%s/%s" % (constants.MOMENT_PATH , self.id)

        f.save(path_moment + "/cover/"+name+".png")

        return path_url + "/cover/"+name+".png"




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







################################
##### Un prospect ###########
################################

class Prospect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    facebookId = db.Column(db.Integer)
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



        db.session.commit()


    def photo_to_send(self):
        photo = {}

        photo["id"] = self.id
        photo["url_original"] = self.url_original
        photo["url_thumbnail"] = self.url_thumbnail
        photo["taken_by"] = self.user.user_to_send()
        photo["nb_like"] = len(self.likes)

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









