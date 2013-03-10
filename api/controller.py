# -*- coding: utf-8 -*-
from api import db
from models import User, Moment, Invitation, Prospect
from sqlalchemy import or_


# Fonction qui renvoie si un utilisateur existe en fonction de son email
def user_exist_email(email):
	user = User.query.filter_by(email = email).first()

	if user is None:
		return False
	else:
	 	return True

# Fonction qui renvoie si un utilisateur existe en fonction de son email
def user_exist_fb(facebookId):
	user = User.query.filter_by(facebookId = facebookId).first()

	if user is None:
		return False
	else:
	 	return True


##
# Fonction qui dit si un user (depuis un dictionnaire) est present dans moment
#
##

def user_exist(user):

	found_user = None

	if "email" in user:
		found_user = User.query.filter(or_(User.email == user["email"], User.secondEmail == user["email"])).first()

		if found_user is not None:
			return True 

	if "facebookId" in user:
		found_user = User.query.filter_by(facebookId = user["facebookId"]).first()

		if found_user is not None:
			return True 

	if "phone" in user:
		found_user = User.query.filter(or_(User.phone == user["phone"], User.secondPhone == user["phone"])).first()

		if found_user is not None:
			return True 

	if "secondEmail" in user:
		found_user = User.query.filter(or_(User.email == user["secondEmail"], User.secondEmail == user["secondEmail"])).first()

		if found_user is not None:
			return True 

	if "secondPhone" in user:
		found_user = User.query.filter(or_(User.phone == user["secondPhone"], User.secondPhone == user["secondPhone"])).first()

		if found_user is not None:
			return True 

	return False



##
# Fonction qui dit retourne un user en fonction des diff param
#
##

def user_from_dict(user):

	found_user = None

	if "email" in user:
		found_user = User.query.filter(or_(User.email == user["email"], User.secondEmail == user["email"])).first()

		if found_user is not None:
			return found_user 

	if "facebookId" in user:
		found_user = User.query.filter_by(facebookId = user["facebookId"]).first()

		if found_user is not None:
			return found_user 

	if "phone" in user:
		found_user = User.query.filter(or_(User.phone == user["phone"], User.secondPhone == user["phone"])).first()

		if found_user is not None:
			return found_user 

	if "secondEmail" in user:
		found_user = User.query.filter(or_(User.email == user["secondEmail"], User.secondEmail == user["secondEmail"])).first()

		if found_user is not None:
			return found_user 

	if "secondPhone" in user:
		found_user = User.query.filter(or_(User.phone == user["secondPhone"], User.secondPhone == user["secondPhone"])).first()

		if found_user is not None:
			return found_user 

	return found_user



##
# Fonctgion qui recupere un prospect à partir d'un dictionnaire d'information contenant :
# - email
# - facebookId
# - secondEmail
# - phone
# - secondPhone
#
##

def get_prospect(user):

	found_prospect = None


	if "email" in user:
		found_prospect = Prospect.query.filter(or_(Prospect.email == user["email"], Prospect.secondEmail == user["email"])).first()

		if found_prospect is not None:
			return found_prospect 

	if "facebookId" in user:
		found_prospect = Prospect.query.filter_by(facebookId = user["facebookId"]).first()

		if found_prospect is not None:
			return found_prospect 

	if "phone" in user:
		found_prospect = Prospect.query.filter(or_(Prospect.phone == user["phone"], Prospect.secondPhone == user["phone"])).first()

		if found_prospect is not None:
			return found_prospect 

	if "secondEmail" in user:
		found_prospect = Prospect.query.filter(or_(Prospect.email == user["secondEmail"], Prospect.secondEmail == user["secondEmail"])).first()

		if found_prospect is not None:
			return found_prospect 

	if "secondPhone" in user:
		found_prospect = Prospect.query.filter(or_(Prospect.phone == user["secondPhone"], Prospect.secondPhone == user["secondPhone"])).first()

		if found_prospect is not None:
			return found_prospect 

	return found_prospect


#Fonction qui renvoit les nb_moments futurs du user ayant l'email email_user
def get_moments_of_user(email_user, nb_moments):

	moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.email==email_user).limit(nb_moments).all()

	return moments


