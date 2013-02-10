# -*- coding: utf-8 -*-
import os
import variables
import datetime
import string
import random
import models
import ssl
import json
import socket
import struct
import binascii
from gcm import GCM
from apns import APNs, Payload
from api import apns



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


##
#
# Depuis une date en string du format : YYYY-MM-DD, on transforme en objet datetime.date
#
##

def cast_date(date):
	dateTemp = date.split("-")
	
	if len(dateTemp) == 3:
		dateTransformed = datetime.date(int(dateTemp[0]), int(dateTemp[1]), int(dateTemp[2]))
		return dateTransformed
	else:
		return None
	


##
#
# Fonction qui transforme une date (datetime.date) en String (YYYY-MM-DD)
#
##

def date_to_string(date):
	dateString = "%s-%s-%s" %(date.year, date.month, date.day)

	return dateString



##
#
# Depuis une heure en string du format : HH:MM, on transforme en objet datetime.time
#
##

def cast_time(time):
	timeTemp = time.split(":")
	timeTransformed = datetime.time(int(timeTemp[0]), int(timeTemp[1]))
	
	return timeTransformed


##
#
# Fonction qui transforme une heure (datetime.time) en String (HH:MM)
#
##

def time_to_string(time):
	timeString = "%s:%s:%s" %(time.hour, time.minute, time.second)

	return timeString


##
# Fonction qui renvoit un identifiant unique de 5 lettres
#
##

def random_identifier():
	letters = string.letters
	identifier = ""

	for i in range (0,6):
		identifier += random.choice(letters[0:26])

	return identifier.upper()


def send_message_device(reg_id, titre, message):
	gcm = GCM("AIzaSyDDA-TLkhjp-WWYPrVs0DznzQc0b77XGO0")
	data = {'titre': titre, 'message': message}

	# Plaintext request
	gcm.plaintext_request(registration_id=reg_id, data=data)

#Push notification to iOS
def send_ios_notif(reg_id, message):
	PAYLOAD = {
			'aps': {
			   	'alert': message,
		    	'sound': 'default'
		}
	}

	payload = json.dumps(PAYLOAD)

	print os.getcwd()

	# Your certificate file
	cert = "api/pushCertificates/cert.pem"
	# APNS development server
	apns_address = ('gateway.sandbox.push.apple.com', 2195)

	# Use a socket to connect to APNS over SSL
	s = socket.socket()
	sock = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_SSLv3, certfile=cert)
	sock.connect(apns_address)

	# Generate a notification packet
	token = binascii.unhexlify(reg_id)
	fmt = '!cH32sH{0:d}s'.format(len(payload))
	cmd = '\x00'
	message = struct.pack(fmt, cmd, len(token), token, len(payload), payload)
	sock.write(message)
	sock.close()










