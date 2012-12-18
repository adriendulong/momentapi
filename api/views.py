from flask import request, abort, redirect, url_for
from api import app, db
import json
from bcrypt import hashpw, gensalt
from api.models import User

@app.route('/')
def index():
	user = User.query.filter(User.username == 'adriendulong').first()
	if user is None:
		return "Rien"
	else:
		return user.email


#Methode pour creer un nouveau user
@app.route('/register', methods=["GET", "POST"])
def register():
	#On verifie que tous les champs sont renseignes
	if request.method == "POST" and "username" in request.form and "password" in request.form and "email" in request.form and "age" in request.form :

		#On recupere toutes les variable
		username = request.form["username"]
		password = request.form["password"]
		hashpwd = hashpw(password, gensalt())
		email = request.form["email"]

		#On verifie que age soit bien au format int
		try:
			age = int(request.form["age"])
		except ValueError:
			abort(400)

		#On cree l'utilisateur
		user = User(username, email, age, hashpwd)

		#On l ajoute en base
		db.session.add(user)
		db.session.commit()

		reponse = {}
		reponse["username"] = username
		reponse["password"] = password
		reponse["hashpwd"] = hashpwd
		reponse["email"] = email
		reponse["age"] = age

		return json.dumps(reponse)

	else:
		abort(400)

