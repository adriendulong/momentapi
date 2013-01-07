from api import db
from models import User, Moment, Invitation


# Fonction qui renvoie si un utilisateur existe en fonction de son email
def user_exist(email):
	user = User.query.filter_by(email = email).first()

	if user is None:
		return False
	else:
	 	return True


#Fonction qui renvoit les nb_moments futurs du user ayant l'email email_user
def get_moments_of_user(email_user, nb_moments):

	moments = Moment.query.join(Moment.guests).join(Invitation.user).filter(User.email==email_user).limit(nb_moments).all()

	return moments


