# -*- coding: utf-8 -*-
import os
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
from api import app
from mail import Mail
import user.userConstants as userConstants
import constants




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




#######################################
#######################################
########## NOTIFICATIONS ##############
#######################################
#######################################




#Push notification to iOS
def send_ios_notif(id_moment, type_notif, reg_id, message, nb_notif_unread):
	'''PAYLOAD = {
			'aps': {
			   	'alert': message,
		    	'sound': 'bingbong.aiff'
			},
			'type_id' : type_notif,
			'id_moment': id_moment
	}


	payload = json.dumps(PAYLOAD)

	print os.getcwd()

	# Your certificate file
	cert = app.root_path+"/pushCertificates/cert.pem"
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
	sock.close()'''


	apns = APNs(use_sandbox=True, cert_file=app.root_path+'/pushCertificates/MomentCert.pem', key_file=app.root_path+'/pushCertificates/MomentKey.pem')

	# Send a notification
	token_hex = reg_id
	payload = Payload(alert=unicode(message, "utf-8"), sound="default", badge=nb_notif_unread)
	apns.gateway_server.send_notification(token_hex, payload)



#Push notification to iOS
def send_ios_notif_chat(id_moment, type_notif, reg_id, message, chat_id, nb_notif_unread):

	apns = APNs(use_sandbox=True, cert_file=app.root_path+'/pushCertificates/MomentCert.pem', key_file=app.root_path+'/pushCertificates/MomentKey.pem')

	#ON limite la taille du message
	if len(message) > 100:
		message = message[0:100]

	# Send a notification
	token_hex = reg_id
	payload = Payload(alert=unicode(message, "utf-8"), sound="default", badge=nb_notif_unread, custom={'type_id': type_notif, 'id_moment' : id_moment, 'chat_id' : chat_id})
	apns.gateway_server.send_notification(token_hex, payload)


	# Get feedback messages
	for (token_hex, fail_time) in apns.feedback_server.items():
	    print token_hex
	    print fail_time


#Push notif ios for a new follower
def send_ios_follower_notif(reg_id, message, id_user, nb_notif_unread):
	apns = APNs(use_sandbox=True, cert_file=app.root_path+'/pushCertificates/MomentCert.pem', key_file=app.root_path+'/pushCertificates/MomentKey.pem')

	#ON limite la taille du message
	if len(message) > 100:
		message = message[0:100]

	# Send a notification
	token_hex = reg_id
	payload = Payload(alert=unicode(message, "utf-8"), sound="default", badge=nb_notif_unread, custom={'type_id': userConstants.NEW_FOLLOWER, 'user_id' : id_user})
	apns.gateway_server.send_notification(token_hex, payload)


	# Get feedback messages
	for (token_hex, fail_time) in apns.feedback_server.items():
	    print token_hex
	    print fail_time







#######################################
#######################################
################ AWS S3 ###############
#######################################
#######################################

def upload_file_S3(path, file_name, extension, f, is_public):

	#The key 
	keyString = path+file_name+"."+extension

	#Headers
	headers = {}
	headers["Content-Type"] = "image/jpeg"

	#Connect to S3
	s3 = boto.connect_s3()

	#We connect to our bucket
	mybucket = s3.get_bucket('apimoment')

	#We get the Key which correspond t
	myKey = mybucket.get_key(keyString)

	#If the key does not exist, we create it
	if myKey is None:
		myKey = mybucket.new_key(keyString)

	#Then we upload the file
	reponse = myKey.set_contents_from_file(f, headers = headers)

	#If it needs to be readeable
	myKey.set_acl('public-read')

	print reponse



#######################################
#######################################
################ MAIL ###############
#######################################
#######################################


def send_inscrption_mail(firstname, lastname, mail):

	m = Mail()

	subject = "Confirmation Inscrption"

	template_name = constants.INSCRIPTION_TEMPLATE

	template_args = []

	destArray = []
	dest = {
		"email" : mail,
		"name" : firstname + " " + lastname
	}
	destArray.append(dest)

	m.send_template(subject, template_name, template_args, destArray)


#Fonction qui va envoyer un mail d'invitation à chaque participants
# user_infos (dict)
#	user_infos.firstname
#	user_infos.lastname
#	user_infos.photo
# to_dest (array)
#	dest (dict)
#		dest.name
#		dest.email
# moment_name (string)

def send_invitation_mail(to_dest, moment_name, user_infos):

	m = Mail()

	contenu = unicode('Invitation à','utf-8')
	subject = "%s %s" % (contenu, moment_name)

	template_name = constants.INVITATION_TEMPLATE

	template_args = []

	#Global Var
	global_merge_vars = []

	global_firstname = {
		"name" : "host_firstname",
		"content" : user_infos["firstname"]
	}

	global_merge_vars.append(global_firstname)

	global_lastname = {
		"name" : "host_lastname",
		"content" : user_infos["lastname"]
	}

	global_merge_vars.append(global_lastname)

	global_photo = {
		"name" : "host_photo",
		"content" : user_infos["photo"]
	}

	global_merge_vars.append(global_photo)


	global_moment = {
		"name" : "moment_name",
		"content" : moment_name
	}

	global_merge_vars.append(global_moment)






	m.send_template(subject, template_name, template_args, to_dest, global_merge_vars)












