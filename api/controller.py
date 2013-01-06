from api import db
from models import User


# Fonction qui renvoie si un utilisateur existe en fonction de son email
def user_exist(email):
	user = User.query.filter_by(email = email).first()

	if user is None:
		return False
	else:
	 	return True