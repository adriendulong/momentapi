# -*- coding: utf-8 -*-

import datetime
from flask import request, abort, redirect, url_for, jsonify
from api import app, db, login_manager
import json
from bcrypt import hashpw, gensalt
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from api.models import User, Moment, Invitation
from itsdangerous import URLSafeSerializer
import controller
import constants
import fonctions




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

	#On verifie que tous les champs obligatoires sont renseignés (email, password, firstname, lastname)
	if request.method == "POST" and "password" in request.form and "email" in request.form and "firstname" in request.form and "lastname" in request.form :

		#On recupere toutes les variable
		password = request.form["password"]
		hashpwd = hashpw(password, gensalt())
		email = request.form["email"]
		firstname = request.form["firstname"]
		lastname = request.form["lastname"]

		# Si un utilisateur avec cette adresse mail existe on ne peut pas créer un compte
		if controller.user_exist(email):
			print "does exist"
			reponse["error"] = "already exist"
			return jsonify(reponse), 405
		else:
			#On cree l'utilisateur
			user = User(email, firstname, lastname, hashpwd)

			#Pour les champs non obligatoires, si ils y sont on les recupere
			if "phone" in request.form:
				phone = request.form["phone"]
				user.phone = phone
			if "facebookId" in request.form:
				facebookId = request.form["facebookId"]
				user.facebookId = facebookId
			if "secondEmail" in request.form:
				secondEmail = request.form["secondEmail"]
				user.secondEmail = secondEmail
			if "secondPhone" in request.form:
				secondPhone = request.form["secondPhone"]
				user.secondPhone = secondPhone

			#On l ajoute en base
			db.session.add(user)
			db.session.commit()
			
			#Maintenant qu'on a l'id on enregistre la photo de profil
			
			if "photo" in request.files:
				f = request.files["photo"]
				#On enregistre la photo et son chemin en base
				name_picture = "%s" % user.id
				path_photo = user.add_profile_picture(f, name_picture)
				user.profile_picture_url = "%s%s" % (app.config.get("SERVER_NAME"), path_photo)
				user.profile_picture_path = "%s%s" % (app.root_path, path_photo)

			#else:
			#	print "Pas de photo"

			#On logge le user. On lui renvoit ainsi le token qu'il doit utiliser
			login_user(user)

			reponse["id"] = user.id
			'''reponse["password"] = password
			reponse["hashpwd"] = hashpwd
			reponse["firstname"] = firstname
			reponse["lastname"] = lastname
			reponse["profile_picture_url"] = user.profile_picture_url'''

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
				login_user(user)
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
		startDateTemp = request.form["startDate"].split("-")
		startDate = datetime.date(int(startDateTemp[0]), int(startDateTemp[1]), int(startDateTemp[2]))

		endDateTemp = request.form["endDate"].split("-")
		endDate = datetime.date(int(endDateTemp[0]), int(endDateTemp[1]), int(endDateTemp[2]))



		#On créé un nouveau moment
		moment = Moment(name, address, startDate, endDate)

		##
		# Recuperation des autres valeurs (non obligatoires)
		##
		if "placeInformations" in request.form:
			placeInformations = request.form["placeInformations"]
			moment.placeInformations = placeInformations
		if "startTime" in request.form:
			startTimeTemp = request.form["startTime"].split(":")
			moment.startTime = datetime.time(int(startTimeTemp[0]), int(startTimeTemp[1]))
		if "endTime" in request.form:
			endTimeTemp = request.form["endTime"].split(":")
			moment.endTime = datetime.time(int(endTimeTemp[0]), int(endTimeTemp[1]))
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
		invitation = Invitation(0, user) 

		#On ratache cette invitations aux guests du nouveau Moment
		moment.guests.append(invitation)

		#On enregistre en base
		db.session.add(moment)
		db.session.commit()

		#On créé tous les chemins necessaires au Moment (pour la sauvegarde des photos et de la cover)
		moment.create_paths()

		reponse["success"] = "Moment created and the owner is %s" % user.email
		return json.dumps(reponse), 200

	else:
		reponse["error"] = "mandatory value missing"
		return json.dumps(reponse), 405








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

	user = User.query.filter_by(email = current_user.email).first()
	moments_of_user = user.get_moments(10)

	# On construit le tableau de moments que l'on va renvoyer
	reponse["moments"] = []
	for moment in moments_of_user:
		# Pour chacun des Moments on injecte que les données que l'on renvoit, et sous la bonne forme
		reponse["moments"].append(moment.moment_to_send())

	reponse["success"] = "OK"

	return jsonify(reponse), 200


#####################################################################
################  Ajouter des invités à un Moment ###################
######################################################################
# Methode acceptées : POST
# Paramètres obligatoires : 
#	- idMoment, array de User 

@app.route('/newguests', methods=["POST"])
def new_guests():
	#On créé la réponse qui sera envoyé
	reponse = {}
	print request.json["idMoment"]

	if "idMoment" in request.json and "users" in request.json:
		print "ok"

		#On vérifie que le user qui envoit ces invitations est autorisé à inviter
		# A faire lorsque j'aurai mis en place si le Moment est ouvert (invitation de tout le monde ou pas)


		# On recupere le Moment en question
		moment = Moment.query.get(int(request.json["idMoment"]))
		print moment.name

		# On recupere les users fournis dans la requete
		users = request.json["users"]
		print len(users)

		for user in users:
			print "hello"
			if "email" in user:
				print user["email"]
			elif "facebookId" in user:
				print user["facebookId"]


		return "ok"


	else:
		reponse["error"] = "mandatory value missing"
		return json.dumps(reponse), 405




#####################################################################
########  Requete pour récupérer les infos d'un user ###############
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

	reponse["id"] = user.id
	reponse["firstname"] = user.firstname
	reponse["lastname"] = user.lastname
	reponse["email"] = user.email
	reponse["profile_picture_url"] = user.profile_picture_url

	return jsonify(reponse), 200








