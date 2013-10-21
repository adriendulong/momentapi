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
from sqlalchemy import func
from twitter import TwitterStream, OAuth
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


def get_timestamp(date, time):
    if time is None:
        time = datetime.time(0,0,0)
    d = datetime.datetime.combine(date, time)
    return d.strftime("%s")

def get_datetime(date, time):
    if time is not None:
        return datetime.datetime.combine(date, time)
    else:
        return datetime.datetime(date.year, date.month, date.day)



#######################################
#######################################
###### NOTIFICATIONS ANDROID ###########
#######################################
#######################################



def send_message_device(reg_id, titre, message):
    gcm = GCM("AIzaSyDDA-TLkhjp-WWYPrVs0DznzQc0b77XGO0")
    data = {"data":[{'titre': titre, 'message': message}]}
    reg_ids = [reg_id]

    # JSON request
    gcm.json_request(registration_ids=reg_ids, data=data)

def send_message_device_chat(reg_id, titre, message, type_notif, moment_id, chat_id):
    gcm = GCM("AIzaSyDDA-TLkhjp-WWYPrVs0DznzQc0b77XGO0")
    data = {"data":[{'titre': titre, 'message': message, "type_notif":type_notif, "moment_id": moment_id, "chat_id":chat_id}]}
    reg_ids = [reg_id]

    # JSON request
    gcm.json_request(registration_ids=reg_ids, data=data)

def send_message_device_photo(reg_id, titre, message, type_notif, moment_id, photo_id):
    gcm = GCM("AIzaSyDDA-TLkhjp-WWYPrVs0DznzQc0b77XGO0")
    data = {"data":[{'titre': titre, 'message': message, "type_notif":type_notif, "moment_id": moment_id, "photo_id":photo_id}]}
    reg_ids = [reg_id]

    # JSON request
    gcm.json_request(registration_ids=reg_ids, data=data)

def send_message_device_invit(reg_id, titre, message, type_notif, moment_id):
    gcm = GCM("AIzaSyDDA-TLkhjp-WWYPrVs0DznzQc0b77XGO0")
    data = {"data":[{'titre': titre, 'message': message, "type_notif":type_notif, "moment_id": moment_id}]}
    reg_ids = [reg_id]

    # JSON request
    gcm.json_request(registration_ids=reg_ids, data=data)





#######################################
#######################################
########## NOTIFICATIONS IOS ##############
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

    apns = APNs(use_sandbox=constants.SANDBOX, cert_file=app.root_path+constants.CERT_PUSH, key_file=app.root_path+constants.KEY_PUSH)

    # Send a notification
    payload = Payload(alert=message, sound="default", badge=nb_notif_unread, custom={'type_id':type_notif, 'id_moment':id_moment})
    #print reg_id
    apns.gateway_server.send_notification(reg_id, payload)

    for (token_hex, fail_time) in apns.feedback_server.items():
	    print token_hex
	    print fail_time




#Push notification to iOS
def send_ios_notif_chat(id_moment, type_notif, reg_id, message, chat_id, nb_notif_unread):

	apns = APNs(use_sandbox=constants.SANDBOX, cert_file=app.root_path+constants.CERT_PUSH, key_file=app.root_path+constants.KEY_PUSH)

	#ON limite la taille du message
	if len(message) > 100:
		message = message[0:150]

	# Send a notification
	token_hex = reg_id
	payload = Payload(alert=message, sound="default", badge=nb_notif_unread, custom={'type_id': type_notif, 'id_moment' : id_moment, 'chat_id' : chat_id})
	apns.gateway_server.send_notification(token_hex, payload)


	# Get feedback messages
	for (token_hex, fail_time) in apns.feedback_server.items():
	    print token_hex
	    print fail_time


#Push notif ios for a new follower
def send_ios_follower_notif(reg_id, message, id_user, nb_notif_unread):
	apns = APNs(use_sandbox=constants.SANDBOX, cert_file=app.root_path+constants.CERT_PUSH, key_file=app.root_path+constants.KEY_PUSH)

	#ON limite la taille du message
	if len(message) > 100:
		message = message[0:100]

	# Send a notification
	token_hex = reg_id
	payload = Payload(alert=message, sound="default", badge=nb_notif_unread, custom={'type_id': userConstants.NEW_FOLLOWER, 'user_id' : id_user})
	apns.gateway_server.send_notification(token_hex, payload)


	# Get feedback messages
	for (token_hex, fail_time) in apns.feedback_server.items():
	    print token_hex
	    print fail_time

####
## Send a simple message
####

def send_ios_simple_message(reg_id, message, nb_notif_unread):
    apns = APNs(use_sandbox=constants.SANDBOX, cert_file=app.root_path+constants.CERT_PUSH, key_file=app.root_path+constants.KEY_PUSH)

    #ON limite la taille du message
    if len(message) > 300:
        message = message[0:300]

    # Send a notification
    token_hex = reg_id
    payload = Payload(alert=unicode(message, "utf-8"), sound="default", badge=nb_notif_unread+1)
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




#######################################
#######################################
################ MAIL ###############
#######################################
#######################################


def send_inscrption_mail(firstname, lastname, mail):

	m = Mail()

	subject = "Confirmation Inscription"

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

def send_invitation_mail(to_dest, moment_name, user_infos, moment_url, description, moment_day, moment_month):

    m = Mail()

    contenu = unicode('vous invite à','utf-8')
    subject = "%s" % (moment_name)

    template_name = constants.INVITATION_TEMPLATE

    template_args = []

    #Global Var
    global_merge_vars = []

    user_name = user_infos["firstname"]+" "+user_infos["lastname"]

    global_name = {
        "name" : "host_name",
        "content" :user_name
    }

    global_merge_vars.append(global_name)


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


    global_moment_url = {
        "name" : "moment_url",
        "content" : moment_url
    }

    global_merge_vars.append(global_moment_url)

    global_moment_description = {
        "name" : "moment_descri",
        "content" : "%s" % description
    }

    global_merge_vars.append(global_moment_description)

    global_moment_day = {
        "name" : "moment_day",
        "content" : moment_day
    }

    global_merge_vars.append(global_moment_day)

    global_moment_momth = {
        "name" : "moment_month",
        "content" : constants.MONTH_YEAR_FR[moment_month]
    }

    global_merge_vars.append(global_moment_momth)



    m.send_template_with_from_name(subject, user_name, template_name, template_args, to_dest, global_merge_vars)



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

def send_invitation_to_prospect_mail(to_dest, moment_name, user_infos, moment_url, description, moment_day, moment_month):

    m = Mail()

    contenu = unicode('vous invite à','utf-8')
    subject = "%s" % (moment_name)

    template_name = constants.INVITATION_PROSPECT_TEMPLATE

    template_args = []

    #Global Var
    global_merge_vars = []

    user_name = user_infos["firstname"]+" "+user_infos["lastname"]

    global_name = {
        "name" : "host_name",
        "content" :user_name
    }

    global_merge_vars.append(global_name)


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


    global_moment_url = {
        "name" : "moment_url",
        "content" : moment_url
    }

    global_merge_vars.append(global_moment_url)

    global_moment_description = {
        "name" : "moment_descri",
        "content" : "%s" % description
    }

    global_merge_vars.append(global_moment_description)

    global_moment_day = {
        "name" : "moment_day",
        "content" : moment_day
    }

    global_merge_vars.append(global_moment_day)

    global_moment_momth = {
        "name" : "moment_month",
        "content" : constants.MONTH_YEAR_FR[moment_month]
    }

    global_merge_vars.append(global_moment_momth)



    m.send_template_with_from_name(subject, user_name, template_name, template_args, to_dest, global_merge_vars)





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

def send_single_photo_mail(to_dest, moment_name, user_infos, photo_url, nb_photo_moment, unique_url):

    m = Mail()

    contenu = unicode(' : Nouvelle photo','utf-8')
    subject = "%s %s" % ( moment_name, contenu)

    template_name = constants.SINGLE_PHOTO_TEMPLATE

    template_args = []

    #Global Var
    global_merge_vars = []

    name = "%s %s" % (user_infos["firstname"], user_infos["lastname"])

    global_user_name = {
        "name" : "user_name",
        "content" : name
    }

    global_merge_vars.append(global_user_name)

    global_firstname = {
        "name" : "fn_user",
        "content" : user_infos["firstname"]
    }

    global_merge_vars.append(global_firstname)

    global_user_photo = {
        "name" : "user_photo",
        "content" : user_infos["photo"]
    }

    global_merge_vars.append(global_user_photo)

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

    global_nb_photo = {
        "name" : "nb_photo",
        "content" : nb_photo_moment
    }

    global_merge_vars.append(global_nb_photo)

    global_unique_url = {
        "name" : "unique_url",
        "content" : unique_url
    }

    global_merge_vars.append(global_unique_url)


    m.send_template(subject, template_name, template_args, to_dest, global_merge_vars)


#Fonction qui va envoyer un mail lorsque une photo est postée
# photos (array of photos url)
# photos_unique (array of unique photos url)
# to_dest (array)
#	dest (dict)
#		dest.name
#		dest.email
# moment_name (string)

def send_multiple_photo_mail(to_dest, moment_name, photos, photos_unique):

    m = Mail()

    contenu = unicode(' : 6 Nouvelles Photos !','utf-8')
    subject = "%s %s" % ( moment_name, contenu)

    template_name = constants.MULTIPLE_PHOTO_TEMPLATE

    template_args = []

    #Global Var
    global_merge_vars = []


    #For each photo we send the url
    count = 1
    for photo in photos:
        name = "photo_url_%s" % count
        global_photo = {
            "name" : name,
            "content" : photo
        }

        count += 1

        global_merge_vars.append(global_photo)

    countUnique = 1
    for photoUnique in photos_unique:
        name = "photo_unique_%s" % countUnique
        global_photo_unique = {
            "name" : name,
            "content" : photoUnique
        }

        countUnique += 1

        global_merge_vars.append(global_photo_unique)

    global_nb_photos = {
        "name" : "nb_photos",
        "content" : len(photos)
    }

    global_merge_vars.append(global_nb_photos)


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


#####
## RAPPORT CRONTAB
#####

def send_report_cron(to_dest, time_spent, nb_moment, nb_users):

    m = Mail()

    contenu = unicode("Rapport du crontab",'utf-8')
    subject = "%s" % contenu

    template_name = constants.REPORT_CRON

    template_args = []

    #Global Var
    global_merge_vars = []

    global_time_spent = {
        "name" : "time_spent",
        "content" : time_spent
    }

    global_nb_moment = {
        "name" : "nb_moment",
        "content" : nb_moment
    }

    global_nb_users = {
        "name" : "nb_user",
        "content" : nb_users
    }

    global_merge_vars.append(global_time_spent)
    global_merge_vars.append(global_nb_moment)
    global_merge_vars.append(global_nb_users)



    m.send_template(subject, template_name, template_args, to_dest, global_merge_vars)


#####
## RAPPORT STATS
#####

def send_report_stats(to_dest, time_spent, env, stats):

    m = Mail()

    contenu = unicode("Stats du ",'utf-8')
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    subject = "%s %s" % (contenu, yesterday.strftime("%d/%m/%y"))

    template_name = constants.MAIL_STATS

    template_args = []

    #Global Var
    global_merge_vars = []

    global_nb_new_moments = {
        "name" : "new_moments",
        "content" : stats["new_moments"]
    }

    global_nb_moments_total = {
        "name" : "nb_moments_total",
        "content" : stats["nb_moments_total"]
    }

    global_nb_fb_events = {
        "name" : "fb_events",
        "content" : stats["fb_events"]
    }

    global_nb_fb_events_total = {
        "name" : "fb_events_total",
        "content" : stats["fb_events_total"]
    }

    global_new_users = {
        "name" : "new_users",
        "content" : stats["new_users"]
    }

    global_users_total = {
        "name" : "users_total",
        "content" : stats["users_total"]
    }

    global_new_invits = {
        "name" : "new_invits",
        "content" : stats["new_invits"]
    }

    global_total_invits = {
        "name" : "total_invits",
        "content" : stats["total_invits"]
    }

    global_photos_new = {
        "name" : "photos_new",
        "content" : stats["photos_new"]
    }

    global_photos_total = {
        "name" : "photos_total",
        "content" : stats["photos_total"]
    }

    global_time_spent = {
        "name" : "time_spent",
        "content" : time_spent
    }

    global_env = {
        "name" : "env",
        "content" : env
    }

    global_merge_vars.append(global_nb_new_moments)
    global_merge_vars.append(global_nb_moments_total)
    global_merge_vars.append(global_nb_fb_events)
    global_merge_vars.append(global_nb_fb_events_total)
    global_merge_vars.append(global_new_users)
    global_merge_vars.append(global_users_total)
    global_merge_vars.append(global_new_invits)
    global_merge_vars.append(global_total_invits)
    global_merge_vars.append(global_photos_new)
    global_merge_vars.append(global_photos_total)
    global_merge_vars.append(global_time_spent)
    global_merge_vars.append(global_env)



    m.send_template(subject, template_name, template_args, to_dest, global_merge_vars)



#####
## SEND INFO BDE
#####

def send_bde_infos(infos):

    m = Mail()

    subject = "Mail pour concours BDE"

    template_name = "bde-challenge"

    template_args = []

    #Global Var
    global_merge_vars = []

    global_name_event = {
        "name" : "name_event",
        "content" : infos["name_event"]
    }

    global_email_compte= {
        "name" : "email_compte",
        "content" : infos["email_compte"]
    }

    global_date_event = {
        "name" : "date_event",
        "content" : infos["date_event"]
    }

    global_description_event = {
        "name" : "description_event",
        "content" : infos["description_event"]
    }

    global_student_name = {
        "name" : "student_name",
        "content" : infos["student_name"]
    }

    global_assos_name = {
        "name" : "assos_name",
        "content" : infos["assos_name"]
    }

    global_assos_email = {
        "name" : "assos_email",
        "content" : infos["assos_email"]
    }

    global_tel_assos = {
        "name" : "tel_assos",
        "content" : infos["tel_assos"]
    }

    global_merge_vars.append(global_name_event)
    global_merge_vars.append(global_email_compte)
    global_merge_vars.append(global_date_event)
    global_merge_vars.append(global_description_event)
    global_merge_vars.append(global_student_name)
    global_merge_vars.append(global_assos_name)
    global_merge_vars.append(global_assos_email)
    global_merge_vars.append(global_tel_assos)

    to_dests = []
    dest = {
        "email" : "hello@appmoment.fr",
        "name" : "Moment"
    }
    to_dests.append(dest)



    m.send_template(subject, template_name, template_args, to_dests, global_merge_vars)


#######################################
#######################################
############# INSTAGRAM ###############
#######################################
#######################################

## A FAIRE :
# 	- Verifier si un moment avec ce hashtag a lieu dans un jour, a lieu ou est fini depuis moins de 1 jour

def update_moment_tag(update):

    print update


    hashtag = update["object_id"]

    #Give the id of concerned Moment
    if hashtag == "paietamoustache" or hashtag=="payetamoustache":
        moment = models.Moment.query.get(8364)
    else:
        print "HASHTAG : "+hashtag.lower()
        moment = models.Moment.query.filter(func.lower(models.Moment.hashtag) == hashtag).first()

    #Instagram API
    api = InstagramAPI(client_id=constants.INSTAGRAM_CLIENT_ID, client_secret=constants.INSTAGRAM_CLIENT_SECRET)
    medias = api.tag_recent_media(count =1, tag_name = hashtag)

    #On créé une nouvelle photo
    photo = models.Photo()

    for media in medias[0]:
        photo.save_instagram_photo(media)


    db.session.add(photo)
    db.session.commit()

    moment.photos.append(photo)
    db.session.commit()



def create_real_time(hashtag):
    api = InstagramAPI(client_id=constants.INSTAGRAM_CLIENT_ID, client_secret=constants.INSTAGRAM_CLIENT_SECRET)

    if app.config["TYPE"] == 0:
        callback_url = constants.API_DEV_URL + "updateinstagram/tag"
    else:
        callback_url =  constants.API_PROD_URL + "updateinstagram/tag"

    api.create_subscription(object='tag', object_id=hashtag, aspect='media', callback_url=callback_url)


def remove_real_time(id_tag):
    api = InstagramAPI(client_id=constants.INSTAGRAM_CLIENT_ID, client_secret=constants.INSTAGRAM_CLIENT_SECRET)
    api.delete_subscriptions(id=id_tag)

def list_sub():
    api = InstagramAPI(client_id=constants.INSTAGRAM_CLIENT_ID, client_secret=constants.INSTAGRAM_CLIENT_SECRET)
    return api.list_subscriptions()



#######################################
#######################################
############# TWITTER ###############
#######################################
#######################################

def listen_tweets_hashtag(hashtag, moment):

    twitter_stream = TwitterStream(auth=OAuth(
        consumer_key=constants.TWITTER_CONSUMER_KEY,
        consumer_secret=constants.TWITTER_CONSUMER_SECRET,
        token=constants.TWITTER_ACCESS_TOKEN_KEY,
        token_secret=constants.TWITTER_ACCESS_TOKEN_SECRET
    ))
    iterator = twitter_stream.statuses.filter(track=hashtag)

    if moment.endDate is not None:
        endtime = get_datetime(moment.endDate, moment.endTime)
    else:
        endtime = get_datetime(moment.startDate, moment.startTime) + datetime.timedelta(hours = 12)

    momentConcerned = models.Moment.query.get(moment.id)

    for tweet in iterator:
        if "media" in tweet["entities"]:
            print "ADD PHOTO nORMALLY"
            photo = models.Photo()
            photo.save_twitter_photo(tweet)
            db.session.add(photo)
            momentConcerned.photos.append(photo)
            db.session.commit()

        now = datetime.datetime.now()
        if now > endtime:
            break




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
                numero_tel["country"] = phonenumbers.region_code_for_number(number)

                return numero_tel

            else:
                return numero_tel

        except phonenumbers.phonenumberutil.NumberParseException:
            return numero_tel




    #Sinon on doit donner une localisation
    else:
        try:

            number = phonenumbers.parse(phone, "FR")

            #On vérifie que le nombre est valide
            if phonenumbers.is_valid_number(number):
                numero_tel = {}
                numero_tel["number"] = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                numero_tel["country"] = phonenumbers.region_code_for_number(number)

                return numero_tel

            elif phone.startswith("07"):
                numero_tel = {}
                numero_tel["number"] = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                numero_tel["country"] = phonenumbers.region_code_for_number(number)
                return numero_tel

            else:
                return numero_tel


        except phonenumbers.phonenumberutil.NumberParseException:
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



def send_push(phone_type, message):

    allUsers = models.User.query.all()

    for user in allUsers:
        for device in user.devices:
            if device.os == phone_type:
                print device.device_id
                device.notify_simple_message(message)












