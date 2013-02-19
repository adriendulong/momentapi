# -*- coding: utf-8 -*-

import datetime
from flask import request, abort, redirect, url_for, jsonify
from api import app, db, login_manager
import json
from bcrypt import hashpw, gensalt
from flask import session
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from api.models import User, Moment, Invitation, Prospect, Photo, Device, Chat
from itsdangerous import URLSafeSerializer
import controller
import constants
import fonctions
import user.userConstants as userConstants
from sqlalchemy import desc, asc




###################################
###### Flask Login functions ######
####################################

#Login_serializer used to encryt and decrypt the cookie token for the remember
#me option of flask-login
login_serializer = URLSafeSerializer(app.secret_key)

@login_manager.user_loader
def load_user(userid):
    """
    Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return 
    None based on the userid.
    The userid was stored in the session environment by Flask-Login.  
    user_loader stores the returned User object in current_user during every 
    flask request. 
    """
    return User.query.get(userid)


@login_manager.token_loader
def load_token(token):
    """
    Flask-Login token_loader callback. 
    The token_loader function asks this function to take the token that was 
    stored on the users computer process it to check if its valid and then 
    return a User Object if its valid or None if its not valid.
    """

    #The Token itself was generated by User.get_auth_token.  So it is up to 
    #us to known the format of the token data itself.  

    #The Token was encrypted using itsdangerous.URLSafeTimedSerializer which 
    #allows us to have a max_age on the token itself.  When the cookie is stored
    #on the users computer it also has a exipry date, but could be changed by
    #the user, so this feature allows us to enforce the exipry date of the token
    #server side and not rely on the users cookie to exipre. 
    #max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

    #Decrypt the Security Token, data = [username, hashpass]
    data = login_serializer.loads(token)

    #Find the User
    user = User.query.filter_by(email = data[0])

    #Check Password and return user or None
    if user and data[1] == user.pwd:
        return user
    return None







    #######################################################
    ################# REQUETES ############################
    #######################################################






@app.route('/')
@login_required
def index():
	print app.config.get("SERVER_NAME")
	user = User.query.filter(User.email == current_user.email).first()
	if user is None:
		return current_user.email
	else:
		return user.email


#################################################################
######## Requete pour ecouter un tag instagram ##################
##################################################################

@app.route("/addtag/<tag>")
def addtag(tag):
    payload = {'client_id': constants.INTAGRAM_CLIENT_ID, 'client_secret': constants.INSTAGRAM_CLIENT_SECRET, 'object':'tag', 'aspect':'media', 'object_id':tag, 'callback_url':'http://api.appmoment.fr/instagram'}
    r = requests.post("https://api.instagram.com/v1/subscriptions/", data=payload)

    return r.text



#################################################################
######## Requete pour enregistrer un nouvel utilisateur #########
##################################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
#	password, email, firstname, lastname
# Autres paramètres possibles :
#	phone, facebookId, secondEmail, secondPhone

@app.route('/register', methods=["POST"])
def register():

	#On créé la réponse qui sera envoyé
	reponse = {}

	if "model" in request.form:
		print request.form["model"]
	if "os" in request.form:
		print request.form["os"]
	if "os_version" in request.form:
		print request.form["os_version"]
	if "reg_id" in request.form:
		print request.form["reg_id"]

	#On verifie que tous les champs obligatoires sont renseignés (email, password, firstname, lastname)
	if request.method == "POST" and "password" in request.form and "email" in request.form and "firstname" in request.form and "lastname" in request.form :

		#On recupere toutes les variable
		password = request.form["password"]
		hashpwd = hashpw(password, gensalt())
		email = request.form["email"]
		firstname = request.form["firstname"]
		lastname = request.form["lastname"]

		# Si un utilisateur avec cette adresse mail existe on ne peut pas créer un compte
		if controller.user_exist_email(email):
			print "does exist"
			reponse["error"] = "already exist"
			return jsonify(reponse), 405

		#Sinon nouvel utilisateur
		else:

			#On se créé un dictionnaire avec toutes les données
			potential_prospect = {}
			potential_prospect["email"] = email
			if "phone" in request.form:
				potential_prospect["phone"] = request.form["phone"]
			if "facebookId" in request.form:
				potential_prospect["facebookId"] = request.form["facebookId"]



			#Quoi qu'il arrive on créé le user
			#On cree l'utilisateur
			user = User(email, firstname, lastname, hashpwd)

			#On l'enregistre en base pour avoir un id
			db.session.add(user)
			db.session.commit()

			#On recupere le prospect si il existe
			prospect = controller.get_prospect(potential_prospect)

			#On a pas trouvé de prospect, on recupere les autres infos
			if prospect is None:
				#On essaye de remplir les autres champs
				#Pour les champs non obligatoires, si ils y sont on les recupere
				if "phone" in request.form:
					phone = request.form["phone"]
					user.phone = phone
				if "facebookId" in request.form:
					facebookId = request.form["facebookId"]
					user.facebookId = facebookId


			#Il existe un prospect donc il faut tout matcher
			else:
				#Matcher les moments
				prospect.match_moments(user)

				#Si on a pas certains champs dans l'inscirption on peut les recuperer du prospect
				if "phone" in request.form:
					phone = request.form["phone"]
					user.phone = phone
				elif prospect.phone is not None:
					user.phone = prospect.phone

				if "facebookId" in request.form:
					facebookId = request.form["facebookId"]
					user.facebookId = facebookId
				elif prospect.facebookId is not None:
					user.facebookId = prospect.facebookId

				if prospect.secondEmail is not None:
					user.secondEmail = prospect.secondEmail

				if prospect.secondPhone is not None:
					user.secondPhone = prospect.secondPhone

				if prospect.profile_picture_url is not None:
					user.profile_picture_url = prospect.profile_picture_url


				#On supprime le prospect
				db.session.delete(prospect)


			#On rajoute ce device si il n'est pas déjà associé
			if "device_id" in request.form:
				device = user.add_device(request.form["device_id"], request.form["os"], request.form["os_version"], request.form["model"])

				#Si on a déjà l'id de notif 
				if "notif_id" in request.form:
					device.notif_id = request.form["notif_id"]

			

			#On l ajoute en base
			db.session.commit()
			
			#Maintenant qu'on a l'id on enregistre la photo de profil
			
			if "photo" in request.files:
				f = request.files["photo"]
				#On enregistre la photo et son chemin en base
				name_picture = "%s" % user.id
				path_photo = user.add_profile_picture(f, name_picture)
				user.profile_picture_url = "http://%s%s" % (app.config.get("SERVER_NAME"), path_photo)
				user.profile_picture_path = "%s%s" % (app.root_path, path_photo)
				#On enregistre en base
				db.session.commit()

			#On logge le user. On lui renvoit ainsi le token qu'il doit utiliser
			if login_user(user):
				session.permanent = True

			reponse["id"] = user.id

			return jsonify(reponse), 200

	else:
		reponse["error"] = "mandatory value missing"
		return jsonify(reponse), 405





######################################################
########  Requete pour Logger un  user ###############
#######################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
#	password, email
# Autres paramètres possibles :
#	

@app.route('/login', methods=["POST"])
def login():
	#On créé la réponse qui sera envoyé
	reponse = {}

	if "model" in request.form:
		print request.form["model"]
	if "os" in request.form:
		print request.form["os"]
	if "os_version" in request.form:
		print request.form["os_version"]
	if "notif_id" in request.form:
		print request.form["notif_id"]
	if "device_id" in request.form:
		print request.form["device_id"]
	if "lang" in request.form:
		print request.form["lang"]

	#On verifie que tous les champs sont renseignes
	if request.method == "POST" and "email" in request.form and "password" in request.form:
		email = request.form["email"]
		password = request.form["password"]

		#On recupere l utilisateur ayant de username
		user = User.query.filter_by(email = email).first()

		# Si l'utilisateur n'existe pas
		if user is None:
			reponse["error"] = "user does not exist"
			return jsonify(reponse), 401
		else:
			# On verifie que le password hashé correspond bien à celui en base
			if hashpw(password, user.pwd) == user.pwd:
				#On verifie si on nous fournie une langue afin de la modifier
				if "lang" in request.form:
					user.lang = request.form["lang"]
					db.session.commit()

				#On rajoute ce device si il n'est pas déjà associé
				if "device_id" in request.form:
					device = user.add_device(request.form["device_id"], request.form["os"], request.form["os_version"], request.form["model"])

					#Si on a déjà l'id de notif 
					if "notif_id" in request.form:
						device.notif_id = request.form["notif_id"]
						db.session.commit()


				if login_user(user):
					session.permanent = True
					reponse["success"] = "Logged"

				# On recupere les n prochains moments de ce user
				moments = controller.get_moments_of_user(user.email, 10)

				'''
				# On construit le tableau de moments que l'on va renvoyer
				reponse["moments"] = []
				for moment in moments:
					# Pour chacun des Moments on injecte que les données que l'on renvoit, et sous la bonne forme
					reponse["moments"].append(moment.moment_to_send())
				'''
				reponse["id"] = user.id

				return jsonify(reponse), 200
			else:
				reponse["error"] = "wrong password"


				return jsonify(reponse), 401

	else:
		reponse["error"] = "mandatory value missing"
		return jsonify(reponse), 405





######################################################
########  Requete pour céer un moment ###############
#######################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
#	name, address, startDate (YYYY-MM-DD), endDate (YYYY-MM-DD)
# Autres paramètres possibles :
#	placeInformations, startTime, endTime, description, hashtag, facebookId

@app.route('/newmoment', methods=["POST"])
@login_required
def new_moment():
	#On créé la réponse qui sera envoyé
	reponse = {}

	#On verifie que tous les champs sont renseignes
	if request.method == "POST" and "name" in request.form and "address" in request.form and "startDate" in request.form and "endDate" in request.form:
		##
		# Recupération des valeurs obligatoires transmises
		##
		name = request.form["name"]
		address = request.form["address"]

		#On recupere et met en forme la date (doit être au format "YYYY-MM-DD")
		startDate = fonctions.cast_date(request.form["startDate"])

		endDate = fonctions.cast_date(request.form["endDate"])



		#On créé un nouveau moment
		moment = Moment(name, address, startDate, endDate)

		##
		# Recuperation des autres valeurs (non obligatoires)
		##
		if "placeInformations" in request.form:
			placeInformations = request.form["placeInformations"]
			moment.placeInformations = placeInformations
		if "startTime" in request.form:
			moment.startTime = fonctions.cast_time(request.form["startTime"])
		if "endTime" in request.form:
			moment.endTime = fonctions.cast_time(request.form["endTime"])
		if "description" in request.form:
			description = request.form["description"]
			moment.description = description
		if "hashtag" in request.form:
			hashtag = request.form["hashtag"]
			moment.hashtag = hashtag
		if "facebookId" in request.form:
			facebookId = request.form["facebookId"]
			moment.facebookId = facebookId


		# On recupere en base le user qui créé ce Moment
		user = User.query.filter(User.email == current_user.email).first()

		#On créé l'invitation qui le lie à ce Moment
		# Il est owner, donc state à 0
		invitation = Invitation(userConstants.OWNER, user) 

		#On ratache cette invitations aux guests du nouveau Moment
		moment.guests.append(invitation)

		#On enregistre en base
		db.session.add(moment)
		db.session.commit()

		#On créé tous les chemins necessaires au Moment (pour la sauvegarde des photos et de la cover)
		moment.create_paths()

		if "photo" in request.files:
				f = request.files["photo"]
				#On enregistre la photo et son chemin en base
				name_picture = "cover"
				path_photo = moment.add_cover_photo(f, name_picture)
				moment.cover_picture_url = "http://%s%s" % (app.config.get("SERVER_NAME"), path_photo)
				moment.cover_picture_path = "%s%s" % (app.root_path, path_photo)
				#On enregistre en base
				db.session.commit()

		reponse = moment.moment_to_send(user.id)
		return jsonify(reponse), 200

	else:
		reponse["error"] = "mandatory value missing"
		return jsonify(reponse), 405








#####################################################################
########  Requete pour récupérer les moments d'un user ###############
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/moments', methods=["GET"])
@login_required
def moments():
	#On créé la réponse qui sera envoyé
	reponse = {}

	user = User.query.get(current_user.id)
	moments_of_user_futur = user.get_moments_sup_date(10, datetime.date.today(), True)
	moments_of_user_past = user.get_moments_inf_date(10, datetime.date.today(), False)

	# On construit le tableau de moments que l'on va renvoyer
	reponse["moments"] = []
	for moment in moments_of_user_past:
		# Pour chacun des Moments on injecte que les données que l'on renvoit, et sous la bonne forme
		reponse["moments"].append(moment.moment_to_send(current_user.id))

	for moment in moments_of_user_futur:
		# Pour chacun des Moments on injecte que les données que l'on renvoit, et sous la bonne forme
		reponse["moments"].append(moment.moment_to_send(current_user.id))	

	reponse["success"] = "OK"

	return jsonify(reponse), 200



##################################################################################
########  Requete pour récupérer les moments sup ou inf à une date ###############
##################################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
# - Date : YYYY-MM-DD
#	

@app.route('/momentsafter/<date>', methods=["GET"])
@login_required
def moments_after_date(date):
	#On créé la réponse qui sera envoyé
	reponse = {}
	nb_moment = 10

	dateRef = fonctions.cast_date(date)
	user = User.query.get(current_user.id)
	moments = []
	moments_to_send = []

	if dateRef is not None:

		# Si on demande des moments superieur à une date future
		if dateRef > datetime.date.today():
			moments = user.get_moments_sup_date(nb_moment, dateRef, True)
			reponse["success"] = "These are the %s moments after the %s" % (len(moments), date)
			for moment in moments:
				moments_to_send.append(moment.moment_to_send(user.id))

		else:
			moments = user.get_moments_inf_date(nb_moment, dateRef, True)
			reponse["success"] = "These are the %s moments before the %s" % (len(moments), date)
			for moment in moments:
				moments_to_send.append(moment.moment_to_send(user.id))
		


		reponse["moments"] = moments_to_send


		return jsonify(reponse), 200

	else:

		reponse["error"] = "The date is in the wrong format"
		return jsonify(reponse), 405


#####################################################################
########  Requetes pour récupérer ou modifier un moment ###############
######################################################################
# Methode acceptées : GET, POST
# Paramètres obligatoires :
# 	- Aucune 
#	

@app.route('/moment/<int:id>', methods=["GET", "POST"])
@login_required
def moment(id):
	#On créé la réponse qui sera envoyé
	print id
	reponse = {}

	# Si c est une requete POST on modofie le moment
	if request.method == "POST":
		# On recupere le moment
		moment = Moment.query.get(id)

		#Si un moment avec cet id existe
		if moment is not None:

			# Si le user peut modifier le moment
			if moment.can_be_modified_by(current_user.id):
				#On voit quelles valeurs sont présentes et on modifie le moment en fonction
				if "name" in request.form:
					moment.name = request.form["name"]
					reponse["name"] = moment.name
				if "address" in request.form:
					moment.address = request.form["address"]
					reponse["address"] = moment.address
				if "startDate" in request.form:
					moment.startDate = fonctions.cast_date(request.form["startDate"])
					reponse["startDate"] = fonctions.date_to_string(moment.startDate)
				if "endDate" in request.form:
					moment.endDate = fonctions.cast_date(request.form["endDate"])
					reponse["endDate"] = fonctions.date_to_string(moment.endDate)
				if "startTime" in request.form:
					moment.startTime = fonctions.cast_time(request.form["startTime"])
					reponse["startTime"] = fonctions.time_to_string(moment.startTime)
				if "endTime" in request.form:
					moment.endTime = fonctions.cast_time(request.form["endTime"])
					reponse["endTime"] = fonctions.time_to_string(moment.endTime)

				#On enregistre
				db.session.commit()

				return jsonify(reponse), 200

			else:
				reponse["error"] = "Not Authorized"
				return jsonify(reponse), 401

		else:
			reponse["error"] = "Moment doesn't exist"
			return jsonify(reponse), 400
		

	# Sinon on recupere le moment
	elif request.method == "GET":
		moment = Moment.query.get(id)

		#Si le moment existe
		if moment is not None:
			#Si le user fait partie des invité (sinon pas accès à ce moment)
			if moment.is_in_guests(current_user.id):
				reponse = moment.moment_to_send(current_user.id)
			else:
				reponse["error"] = "Not Authorized"
				return jsonify(reponse), 401
			

	return jsonify(reponse), 200


#####################################################################
################  Ajouter des invités à un Moment ###################
######################################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
#	- idMoment, array de User 

@app.route('/newguests/<int:idMoment>', methods=["POST"])
@login_required
def new_guests(idMoment):
	#On créé la réponse qui sera envoyé
	reponse = {}
	print idMoment

	# Compteur d'invités rajoutés
	count = 0

	if "users" in request.json:
		# On recupere le Moment en question
		moment = Moment.query.get(idMoment)

		if moment is not None:


			if moment.can_add_guest(current_user.id):

				# On recupere les users fournis dans la requete
				users = request.json["users"]
				print len(users)

				#On parcourt la liste des users envoyés
				for user in users:
					#On verifie qu'on a des infos sur le user
					if "id" in user or "email" in user or "phone" in user or "facebookId" in user:

						#Si l'id est fourni normalement il existe dans Moment
						# On va donc le chercher et le rajouté en invité
						if "id" in user:
							user_to_add = User.query.get(user["id"])

							#On verfie que le user existe pour le rajouter
							if user_to_add is not None:
								# On le rajoute et si ça s'est bien passé on incrémente le compteur
								if moment.add_guest_user(user_to_add, current_user, userConstants.UNKNOWN):
									count += 1
									print user["id"]


						#Sinon c'est un prospect
						else:
							#On verifie que le user n'existe pas quand meme
							if not controller.user_exist(user):
								prospect = controller.get_prospect(user)

								#Pas de prospect
								if prospect is None:
									##
									prospect = Prospect()
									prospect.init_from_dict(user)
									moment.prospects.append(prospect)
									count += 1

								#Le prospect existe
								else:
									prospect.update(user)
									if moment.add_prospect(prospect):
										count += 1

							#Si il esicte on le recupere
							else:
								moment_user = controller.user_from_dict(user)
								if moment.add_guest_user(moment_user, current_user, userConstants.UNKNOWN):
									count += 1


				#On enregistre en base
				db.session.commit()
				
				reponse["nb_user_added"] = count
				return jsonify(reponse), 200

			else:
				reponse["error"] = "Not Aothorized"
				return jsonify(reponse), 401


		else:
			reponse["error"] = "This Moment does not exist"
			return jsonify(reponse), 405


	else:
		reponse["error"] = "mandatory value missing"
		return jsonify(reponse), 405




#####################################################################
########  Requete pour récupérer les infos d'un user connecté ###############
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/user', methods=["GET"])
@login_required
def user():
	#On créé la réponse qui sera envoyé
	reponse = {}

	user = User.query.get(current_user.id)

	reponse = user.user_to_send()

	return jsonify(reponse), 200


#####################################################################
########  Requete pour récupérer les infos d'un user selon son id ###############
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/user/<int:id>', methods=["GET"])
@login_required
def user_id(id):
	#On créé la réponse qui sera envoyé
	reponse = {}

	user = User.query.get(id)

	reponse = user.user_to_send()

	return jsonify(reponse), 200




#######################################################################################
########  Requete pour modifier le state d'un User pour un moment donné ###############
######################################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/state/<int:moment_id>/<int:state>', methods=["GET"])
@login_required
def modifiy_state(moment_id, state):
	#On créé la réponse qui sera envoyé
	reponse = {}

	user = User.query.get(current_user.id)
	moment = Moment.query.get(moment_id)

	if moment is not None:
		#On verifie que le user est bien dans les invités
		if moment.is_in_guests(current_user.id):
			# On ne modifie que si il n'est pas ADMIN ou OWNER
			if moment.get_user_state(current_user.id) != userConstants.ADMIN and moment.get_user_state(current_user.id) != userConstants.OWNER:
				#On essaye de modifier son état
				if state == userConstants.COMING or state == userConstants.NOT_COMING or state == userConstants.MAYBE:
					moment.modify_user_state(user, state)
					reponse["new_state"] = state

				else:
					reponse["error"] = "This state is not valid. State possibles : 2 = Coming, 3 = Not coming, 5 = Maybe"
					return jsonify(reponse), 405
			else:
				reponse["error"] = "Not Authorized : you can't modify the Admin or Owner state thanks to this request"
				return jsonify(reponse), 401

		else:
			reponse["error"] = "Not Authorized : the user is not a guest of this moment"
			return jsonify(reponse), 401


	else:
		reponse["error"] = "This moment does not exist"
		return jsonify(reponse), 405

	return jsonify(reponse), 200





##########################################################
###############  Ajouter un user en Admin ###############
########################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/admin/<int:moment_id>/<int:user_id>', methods=["GET"])
@login_required
def add_admin(moment_id, user_id):
	#On créé la réponse qui sera envoyé
	reponse = {}

	user = User.query.get(user_id)
	moment = Moment.query.get(moment_id)

	if moment is not None:
		#On verifie que le user qui fait cette requete est soit ADMIN soit OWNER
		if moment.get_user_state(current_user.id) == userConstants.ADMIN or moment.get_user_state(current_user.id) == userConstants.OWNER:
			#On verifie que le user existe bien
			if user is not None:
				#On vérifie que le user est déjà parmis les invités
				if moment.is_in_guests(user_id):
					#On verifie que le user n'est pas déjà owner
					if user != moment.get_owner():
						#Si le user est déjà ADMIN on le passe à COMING
						if moment.is_admin(user):
							moment.modify_user_state(user, userConstants.COMING)
							reponse["success"] = "The user %s %s is no more ADMIN, he is now COMING" % (user.firstname, user.lastname)
						else:
							#Le user devient ADMIN
							moment.modify_user_state(user, userConstants.ADMIN)
							reponse["success"] = "The user %s %s is now the admin of this moment" % (user.firstname, user.lastname)
					else:
						reponse["error"] = "This user is already the owner of this moment"
						return jsonify(reponse), 405
				else:
					reponse["error"] = "Not Authorized : the user is not a guest of this moment"
					return jsonify(reponse), 401

			else:
				reponse["error"] = "The user does not exist"
				return jsonify(reponse), 405
	
		else:
			reponse["error"] = "Not Authorized : only owner or admins of the moment can add an Admin to it"
			return jsonify(reponse), 401

	else:
		reponse["error"] = "This moment does not exist"
		return jsonify(reponse), 405

	return jsonify(reponse), 200






#####################################################################
############ Recupérer les user présents dans Moment ###################
######################################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
#	- array de User avec soit un email, soit un facebookId, soit un phone et aussi soit un secondEmail

@app.route('/usersmoment', methods=["POST"])
@login_required
def users_in_moment():
	#On créé la réponse qui sera envoyé
	reponse = {}
	reponse["moment_users"] = []

	#On liste les User déjà récupéré pour pas en mettre plusieurs fois
	idFound = []

	if "users" in request.json:
		users = request.json["users"]

		#On parcours la liste
		for user in users:
			moment_user = None

			#Si l'email est fourni
			if "email" in user:
				moment_user = User.query.filter_by(email = user["email"]).first()

			#Si on a le facebook Id
			if "facebookId" in user and moment_user is None:
				moment_user = User.query.filter_by(facebookId = user["facebookId"]).first()

			#Si on a le numero de tel
			if "phone" in user and moment_user is None:
				moment_user = User.query.filter_by(phone = user["phone"]).first()

			#Si on a toujours pas de user et qu'on a le secondEmail
			if "secondEmail" in user and moment_user is None:
				moment_user = User.query.filter_by(secondEmail = user["secondEmail"]).first()

			if moment_user is not None:
				reponse["moment_users"].append(moment_user.user_to_send())

		return jsonify(reponse), 200


	else:
		reponse["error"] = "mandatory value missing"
		return jsonify(reponse), 405




######################################################################################
########  Requete pour récupérer les user favoris d'un user authentifié ###############
#####################################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/favoris', methods=["GET"])
@login_required
def favoris():
	#On créé la réponse qui sera envoyé
	reponse = {}
	reponse["favoris"] = []

	#On parcourt les favoris du user
	for fav in current_user.favoris:
		#Si le favoris a le score suffisant
		if fav.score > 5:
			reponse["favoris"].append(fav.the_favoris.user_to_send())

	return jsonify(reponse), 200




######################################################################################
########  Requete pour récupérer les invités à un moment (classé par state) ###############
#####################################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/guests/<int:id_moment>', methods=["GET"])
@login_required
def guests_moment(id_moment):
	#On créé la réponse qui sera envoyé
	reponse = {}
	reponse["owner"] = []
	reponse["admin"] = []
	reponse["coming"] = []
	reponse["not_coming"] = []
	reponse["maybe"] = []
	reponse["unknown"] = []

	moment = Moment.query.get(id_moment)

	if moment is not None:
		#On parcourt tous les invités
		for guest in moment.guests:
			if guest.state == userConstants.OWNER:
				reponse["owner"].append(guest.user.user_to_send())
			elif guest.state == userConstants.ADMIN:
				reponse["admin"].append(guest.user.user_to_send())
			elif guest.state == userConstants.COMING:
				reponse["coming"].append(guest.user.user_to_send())
			elif guest.state == userConstants.NOT_COMING:
				reponse["not_coming"].append(guest.user.user_to_send())
			elif guest.state == userConstants.MAYBE:
				reponse["maybe"].append(guest.user.user_to_send())
			elif guest.state == userConstants.UNKNOWN:
				reponse["unknown"].append(guest.user.user_to_send())

		for prospect in moment.prospects:
			reponse["unknown"].append(prospect.prospect_to_send())

		return jsonify(reponse), 200

	#Ce moment n'existe pas
	else:
		reponse = {}
		reponse["error"] = "This Moment does not exist"
		return jsonify(reponse), 405




#####################################################################
############ Poster une nouvelle photo sur un Moment ###################
######################################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
#	- Une photo

@app.route('/addphoto/<int:moment_id>', methods=["POST"])
@login_required
def new_photos(moment_id):
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	#On recupere le moment en question
	moment = Moment.query.get(moment_id)

	if "photo" in request.files:
		photo = Photo()

		#On enregistre en base l'objet photo
		db.session.add(photo)
		db.session.commit()

		#Puis on enregistre en disque la photo
		photo.save_photo(request.files["photo"], moment, current_user)

		reponse["success"] = photo.photo_to_send()

		return jsonify(reponse), 200

	else:
		reponse["error"] = "no photo received"
		return jsonify(reponse), 405


#####################################################################
############ Retourne la liste des photos prises pour un moment ###################
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/photosmoment/<int:moment_id>', methods=["GET"])
@login_required
def photos_moment(moment_id):
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	#On recupere le moment en question
	moment = Moment.query.get(moment_id)

	if moment is not None:
		#On verifie que le user est bien parmis les invites pour acceder aux photos
		if moment.is_in_guests(current_user.id):
			reponse["photos"] = []
			for photo in moment.photos:
				reponse["photos"].append(photo.photo_to_send())

			return jsonify(reponse), 200

		else:
			reponse["error"] = "This user does not have access to this Moment"
			return jsonify(reponse), 401

	else:
		reponse["error"] = "This moment does not exist"
		return jsonify(reponse), 405


#####################################################################
############ Like une photo ou dislike si déjà liké ######
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/like/<int:photo_id>', methods=["GET"])
@login_required
def like_photo(photo_id):
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	photo = Photo.query.get(photo_id)

	if photo is not None:
		#On verifie que le user fait partie des invités
		if photo.moment.is_in_guests(current_user.id):
			photo.like(current_user)
			reponse["success"] = "Photo liked"
			reponse["nb_likes"] = len(photo.likes)
			return jsonify(reponse), 200

		else:
			reponse["error"] = "The user is not authorized to like this photo"
			return jsonify(reponse), 401

	else:
		reponse["error"] = "This photo does not exist"
		return jsonify(reponse), 405



#####################################################################
############ Post un chat du user loggé ############################
######################################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
# - Dans l'url : id_moment
#  - Dans le corp : message
#	

@app.route('/newchat/<int:moment_id>', methods=["POST"])
@login_required
def new_chat(moment_id):
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	moment = Moment.query.get(moment_id)

	#Si le moment existe
	if moment is not None:
		#On verifie que le user fait partie des invités
		if moment.is_in_guests(current_user.id):
			#Si un message est envoyé
			if "message" in request.form:
				#On créé un nouveau chat lié au user en question et au Moment
				chat = Chat(request.form["message"], current_user, moment)
				

				reponse["success"] = "message added to the chat"
				return jsonify(reponse), 200

			else:
				reponse["error"] = "Mandatory value missing"
				return jsonify(reponse), 405

		else:
			reponse["error"] = "The user is not a guest of this moment"
			return jsonify(reponse), 401

		

	else:
		reponse["error"] = "This moment does not exist"
		return jsonify(reponse), 405


#####################################################################
############ Recuperer les x dernier chat ############################
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/lastchats/<int:moment_id>', methods=["GET"])
@app.route('/lastchats/<int:moment_id>/<int:nb_page>', methods=["GET"])
@login_required
def last_chats(moment_id, nb_page = 1):
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	moment = Moment.query.get(moment_id)

	if moment is not None:
		#On verifie que le user fait partie des invités
		if moment.is_in_guests(current_user.id):
			#On recupere les chats de ce Moment, au format pagination
			print nb_page
			chatsPagination = Chat.query.filter_by(moment_id=moment_id).order_by(desc(Chat.time)).order_by(asc(Chat.id)).paginate(nb_page, constants.CHATS_PAGINATION, False)

			#Si il y a des pages suivantes
			if chatsPagination.has_next:
				reponse["next_page"] = chatsPagination.next_num
			#Si il y a une page precedente
			if chatsPagination.has_prev:
				reponse["prev_page"] = chatsPagination.prev_num

			#On construit le tableau des messages
			reponse["chats"] = []
			for chat in chatsPagination.items:
				reponse["chats"].append(chat.chat_to_send())

			reponse["chats"].reverse()
			return jsonify(reponse), 200



		else:
			reponse["error"] = "The user is not a guest of this moment"
			return jsonify(reponse), 401

	else:
		reponse["error"] = "This moment does not exist"
		return jsonify(reponse), 405



#####################################################################
############ Recuperer un chat ############################
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/chat/<int:chat_id>', methods=["GET"])
@login_required
def chat(chat_id):
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	

	chat = Chat.query.filter(Chat.id==chat_id).first()

	if chat is None:
		reponse["error"] = "This chat does not exist"
		return jsonify(reponse), 405

	else:
		moment = Moment.query.get(chat.moment_id)

		#Le user doit être invité à ce moment
		if moment.is_in_guests(current_user.id):
			#On construit le tableau des messages
			reponse["chat"] = chat.chat_to_send()

			return jsonify(reponse), 200
		else:
			reponse["error"] = "The user is not a guest of this moment"
			return jsonify(reponse), 401




#####################################################################
############ Recuperer les notifications d'un user #################
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/notifications', methods=["GET"])
@login_required
def notifications():
	#On créé la réponse qui sera envoyé
	reponse = {}
	reponse["invitations"] = []
	reponse["new_photos"] = []
	reponse["new_chats"] = []
	reponse["modif_moment"] = []
	
	for notification in current_user.notifications:
		#Les invitations
		if notification.type_notif == userConstants.INVITATION:
			reponse["invitations"].append(notification.notif_to_send())

		#Les nouveaux chats
		if notification.type_notif == userConstants.NEW_CHAT:
			reponse["new_chats"].append(notification.notif_to_send())

		#Les nouvelles photos
		if notification.type_notif == userConstants.NEW_PHOTO:
			reponse["new_photos"].append(notification.notif_to_send())

		#Les modifications
		if notification.type_notif == userConstants.MODIF:
			reponse["modif_moment"].append(notification.notif_to_send())

	return jsonify(reponse), 200


#####################################################################
############ REset Notifications une fois luz #################
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/resetnotifications', methods=["GET"])
@login_required
def reset_notifications():
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	for notification in current_user.notifications:
		db.session.delete(notification)

	db.session.commit()

	reponse["success"] = "Notifications emptied"

	return jsonify(reponse), 200



#####################################################################
############ Matcher les moments avec un code #######################
######################################################################
# Methode acceptées : GET
# Paramètres obligatoires : 
#	

@app.route('/matchcode/<code>', methods=["GET"])
@login_required
def match_code(code):
	#On créé la réponse qui sera envoyé
	reponse = {}
	
	prospect = Prospect.query.filter(Prospect.unique_code == code).first()

	if prospect is None:
		reponse["error"] = "This code does not exist"
		return jsonify(reponse), 405

	else:
		#On recupere les moments
		prospect.match_moments(current_user)
		#On met à jour le profil avec les données sur prospect
		current_user.update_from_prospect(prospect)

		#On efface le prospect
		db.session.delete(prospect)
		db.session.commit()

		reponse["success"] = "The Moments have been matched"
		return jsonify(reponse), 200









