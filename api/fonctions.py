# -*- coding: utf-8 -*-
import os
import variables

##
# Fonction qui renvoit la path du dossier d'un user, ou le créé si il n'existe pas
##

def get_user_dir(idUser):
	#On verifie que le dossier existe
	path_user = "%s%s" % (variables.PROFILE_PATH, idUser)
	if os.path.exists(path_user):
		return path_user
	#Sinon on le créé
	else:
		os.mkdir(path_user)
		return path_user


##
# Fonction qui va rajouté une photo de profile pour un user donné
# Variables :
# 	- f : la photot
# 	- name : le nom sou lequel on enregistrera la photo
#	- id_user : l'id du user 
##

def add_profile_picture(f, name, id_user):
	#On recupere le path du user
	user_path = get_user_dir(id_user)

	# On vérifie que le chemin pour enregistrer sa photo de profil existe
	if os.path.exists(user_path+"/profile_pictures"):
		f.save(user_path+"/profile_pictures/"+name+".png")
		return user_path+"/profile_pictures/"+name+".png"
	#sinon on créé le chemin en question
	else:
		os.mkdir(user_path+"/profile_pictures")
		f.save(user_path+"/profile_pictures/"+name+".png")
		return user_path+"/profile_pictures/"+name+".png"


