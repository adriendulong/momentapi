# -*- coding: utf-8 -*-
from api import app


#######
## PRIVACY MOMENTS
#######

PRIVATE = 0
OPEN = 1
PUBLIC = 2


# Male and Female
MALE = "M"
FEMALE = "F"


##
# WEBSITE URL
##

WEBSITE = "http://appmoment.fr"


##
# DIFFERENT PATHS
##

PROFILE_PATH = "/static/data/users"
AWS_PROFILE_PATH = "data/users/"

MOMENT_PATH = "/static/data/moments"
AWS_MOMENT_PATH = "data/moments/"

TEMP_PATH = "/static/data/tmp"

UNIQUE_PHOTO_URL = "/p/"

UNIQUE_MOMENT_URL = "/mo/"

#Nombre de chat par page
CHATS_PAGINATION = 20

#Nombre de Notif par page
NOTIFS_PAGINATION = 20

#Nombre de chat par page
FEED_PAGINATION = 10

#Tailles photos
SIZE_THUMBNAIL = 250, 250
SIZE_ORIGINAL = 1500, 1500
SIZE_MEDIUM = 700, 700

GCM_APP_KEY = "AIzaSyDDA-TLkhjp-WWYPrVs0DznzQc0b77XGO0"



#############
# AMAZON S3 #
#############

S3_URL = "https://s3-eu-west-1.amazonaws.com"
S3_BUCKET = "/apimoment/"

S3_DEFAULT_COVERS = "https://s3-eu-west-1.amazonaws.com/apimoment/default/default_covers/"


#############
# FACEBOOK #
#############

FB_ACCESS_TOKEN = "445031162214877|haRhQcYEgIPpXc7hzGSbtK3IBfs"
FB_EVENT_VERIFY_TOKEN = "fbeventsMoment"



#############
# MANDRILL #
#############

MANDRILL_API_KEY = "eW9iPysJRI-LBinyq_D_Hg"

FROM_EMAIL = "hello@appmoment.fr"
FROM_NAME = "Moment"

#Templates
INSCRIPTION_TEMPLATE = "Inscription_Moment"
INVITATION_TEMPLATE = "Invitation_Moment"
NEW_PASS_TEMPLATE = "MDP_OUBLIE"
SINGLE_PHOTO_TEMPLATE = "NouvellePhoto"


################
## INSTAGRAM ###
################
INSTAGRAM_CLIENT_ID = "926e99d034a443af9f6a70a1dff69af1"
INSTAGRAM_CLIENT_SECRET = "d05fe5f51ede4f31b88bc797821fb212"
INSTAGRAM_CALLBACK_URL = "http://api.appmoment.fr/updateinstagram/tag" 
