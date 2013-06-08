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
from api import app, db
from mail import Mail
import user.userConstants as userConstants
import constants
from instagram.client import InstagramAPI
import phonenumbers
from phonenumbers.geocoder import area_description_for_number
from phonenumbers.geocoder import country_name_for_number
from phonenumbers.phonenumberutil import region_code_for_number
import shortuuid
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper







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


##
# Fonction qui renvoit un uuid (pratiquement unique)
##

def get_uuid(length = 6):

	return shortuuid.uuid()[:length]


##
# Fonction qui renvoit un nouveau password aléatoire
#
##

def random_pass():
	letters = string.letters
	identifier = ""

	for i in range (0,4):
		identifier += random.choice(letters[0:26])

	identifier += "%s" % random.randint(1, 9) 

	for i in range (0,2):
		identifier += random.choice(letters[0:26])

	return identifier


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
	payload = Payload(alert=unicode(message, "utf-8"), sound="default", badge=nb_notif_unread, custom={'type_id':type_notif, 'id_moment':id_moment})
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





#Fonction qui va envoyer un mail lorsque une photo est postée
# user_infos (dict)
#	user_infos.firstname
#	user_infos.lastname
#	user_infos.photo
# to_dest (array)
#	dest (dict)
#		dest.name
#		dest.email
# moment_name (string)
# photo_url (string)

def send_single_photo_mail(to_dest, moment_name, user_infos, photo_url):

	m = Mail()

	contenu = unicode(' : Nouvelle photo','utf-8')
	subject = "%s %s" % ( moment_name, contenu)

	template_name = constants.SINGLE_PHOTO_TEMPLATE

	template_args = []

	#Global Var
	global_merge_vars = []

	global_firstname = {
		"name" : "fn_user",
		"content" : user_infos["firstname"]
	}

	global_merge_vars.append(global_firstname)

	global_photo = {
		"name" : "image_moment",
		"content" : photo_url
	}

	global_merge_vars.append(global_photo)


	global_moment = {
		"name" : "moment_name",
		"content" : moment_name
	}

	global_merge_vars.append(global_moment)






	m.send_template(subject, template_name, template_args, to_dest, global_merge_vars)



#Fonction qui va envoyer un mail une fois le mdp regéneré
# to_dest (array)
#	dest (dict)
#		dest.name
#		dest.email
# new_pass (string)

def send_new_pass_mail(to_dest, new_pass):

	m = Mail()

	contenu = unicode("Génération d'un nouveau mot de passe ",'utf-8')
	subject = "%s" % contenu

	template_name = constants.NEW_PASS_TEMPLATE

	template_args = []

	#Global Var
	global_merge_vars = []

	global_password = {
		"name" : "new_password",
		"content" : new_pass
	}

	global_merge_vars.append(global_password)



	m.send_template(subject, template_name, template_args, to_dest, global_merge_vars)





#######################################
#######################################
############# INSTAGRAM ###############
#######################################
#######################################

## A FAIRE :
# 	- Verifier si un moment avec ce hashtag a lieu dans un jour, a lieu ou est fini depuis moins de 1 jour

def update_moment_tag(update):

	hashtag = update["object_id"]

	moments = models.Moment.query.filter(models.Moment.hashtag == hashtag).all()
	print len(moments)

	#Instagram API
	api = InstagramAPI(client_id=constants.INSTAGRAM_CLIENT_ID, client_secret=constants.INSTAGRAM_CLIENT_SECRET)
	medias = api.tag_recent_media(count =1, tag_name = hashtag)

	#On créé une nouvelle photo
	photo = models.Photo()

	for media in medias[0]:
		photo.save_instagram_photo(media)
		print media.user.full_name
		print media.images["standard_resolution"].url


	db.session.add(photo)
	db.session.commit()

	moments[0].photos.append(photo)
	db.session.commit()

	print hashtag




#######################################
#######################################
############# TELEPHONE ###############
#######################################
#######################################



#####
## Fonction qui controlle que c'est un numéro au bon format (international, sinon on tente FR)
## et qui renvoit le numero si jamais il est bon, ou None sinon
####


def phone_controll(phone):

	numero_tel = None

	#On controlle qu'il y a un plus au début, sinon il faut donner la localisation
	if phone[0] == "+":

		#Si jamais il y a un pb avec le parsage
		try:
			number = phonenumbers.parse(phone, None)


			#On vérifie que le nombre est valide
			if phonenumbers.is_valid_number(number):
				numero_tel = {}
				numero_tel["number"] = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
				numero_tel["country"] = region_code_for_number(number)

				return numero_tel

			else:
				print "Numéro invalide"
				return numero_tel

		except phonenumbers.phonenumberutil.NumberParseException:
			print "Problème exception"
			return numero_tel


		

	#Sinon on doit donner une localisation
	else:
		print "quelle localisation ?"

		try:

			number = phonenumbers.parse(phone, "FR")

			#On vérifie que le nombre est valide
			if phonenumbers.is_valid_number(number):
				numero_tel = {}
				numero_tel["number"] = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
				numero_tel["country"] = region_code_for_number(number)

				return numero_tel

			else:
				print "Numéro invalide"
				return numero_tel


		except phonenumbers.phonenumberutil.NumberParseException:
			print "Problème exception"
			return numero_tel

########
## Cross Domain decorator
########

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator











