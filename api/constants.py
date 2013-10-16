# -*- coding: utf-8 -*-
from api import app
import fonctions


#######
## PRIVACY MOMENTS
#######

PRIVATE = 0
OPEN = 1
PUBLIC = 2
SPECIAL_EVENT = 3
SPECIAL_EVENT_LIVE = 4


##########
## DELAY PUSH PHOTO
#########

DELAY_PUSH_PHOTO = 120



##########
## FAKE MOMENTS
##########

FAKE_MOMENT_NAME = "Mon premier Moment !"
FAKE_MOMENT_ADDRESS = "Bordeaux, France"
FAKE_MOMENT_DESCRIPTION = "Ceci est votre premier Moment. Le but étant de vous montrer tout ce que vous pourrez faire grâce à cette application. Une soirée, une semaine de vacances, un évènement entre proche, etc. Grace à Moment, invitez vos amies, et partager tous ensemble vos photos, discutez et organisez l'événement dans le chat prévu à cet effet !"
FAKE_MOMENT_COVER = "https://s3-eu-west-1.amazonaws.com/apimoment/default/default_covers/default2.jpg"
FAKE_MOMENT_CHAT = "Bienvenue sur le chat de l'évènement. Discutez, échangez, commentez, organisez votre évènement avec eux !"
FAKE_MOMENT_PHOTO1 = "https://s3-eu-west-1.amazonaws.com/apimoment/default/default_moment/photo1.jpg"
FAKE_MOMENT_PHOTO2 = "https://s3-eu-west-1.amazonaws.com/apimoment/default/default_moment/photo2.jpg"
FAKE_MOMENT_PHOTO3 = "https://s3-eu-west-1.amazonaws.com/apimoment/default/default_moment/photo3.jpg"


# Male and Female
MALE = "M"
FEMALE = "F"


##
# WEBSITE URL
##

WEBSITE = "http://appmoment.fr"

###
## API URL
###

API_DEV_URL = "http://apidev.appmoment.fr/"
API_PROD_URL = "http://api.appmoment.fr/"

##
# DIFFERENT PATHS
##

PROFILE_PATH = "/static/data/users"
AWS_PROFILE_PATH = "data/users/"

MOMENT_PATH = "/static/data/moments"
AWS_MOMENT_PATH = "data/moments/"

TEMP_PATH = "/static/data/tmp"

UNIQUE_PHOTO_URL = "/p/"

if app.config["TYPE"] == 0:
    UNIQUE_MOMENT_URL = "/devmo/"
elif app.config["TYPE"] == 1:
    UNIQUE_MOMENT_URL = "/mo/"

#Nombre de chat par page
CHATS_PAGINATION = 20

#Nombre de Notif par page
NOTIFS_PAGINATION = 20

#Nombre de chat par page
FEED_PAGINATION = 10

#Number of photos per page
PHOTOS_PAGINATION = 30

#Nombre de moments futurs ou passés renvoyés au max
MAX_MOMENTS = 20

#Tailles photos
SIZE_THUMBNAIL = 350, 350
SIZE_ORIGINAL = 1500, 1500
SIZE_MEDIUM = 700, 700

GCM_APP_KEY = "AIzaSyDDA-TLkhjp-WWYPrVs0DznzQc0b77XGO0"



############
# ERRORS ###
############

NOT_CONNECTED = 0


#############
# AMAZON S3 #
#############

S3_URL = "https://s3-eu-west-1.amazonaws.com"

if app.config["TYPE"] == 0:
    S3_BUCKET = "/apimomentdev/"
elif app.config["TYPE"] == 1:
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
INVITATION_TEMPLATE = "invitation-event"
INVITATION_PROSPECT_TEMPLATE = "invitation-event-prospect"
NEW_PASS_TEMPLATE = "motdepasse-oublie-1"
SINGLE_PHOTO_TEMPLATE = "template-photo-x1"
REPORT_CRON = "reportcrontab"
MULTIPLE_PHOTO_TEMPLATE = "template-photo-many"
MAIL_STATS = "mail-stats"



################
## INSTAGRAM ###
################
INSTAGRAM_CLIENT_ID = "926e99d034a443af9f6a70a1dff69af1"
INSTAGRAM_CLIENT_SECRET = "d05fe5f51ede4f31b88bc797821fb212"
INSTAGRAM_CALLBACK_URL = "http://api.appmoment.fr/updateinstagram/tag"

if app.config["TYPE"] == 0:
    INSTAGRAM_USER = 18
elif app.config["TYPE"] == 1:
    INSTAGRAM_USER = 1507


################
## TWITTER #####
################

TWITTER_CONSUMER_KEY = "cRwFsBh6c9iQruAqfE6LIg"
TWITTER_CONSUMER_SECRET = "ExUexrUAvNHx6mdZootqQBjnjKWngVgPQMCaNb60c"
TWITTER_ACCESS_TOKEN_KEY = "1898050556-BtKF8g4kxVC4HjRkbmQukhLTVe6MJyILBNv0noG"
TWITTER_ACCESS_TOKEN_SECRET = "TY3KtJa4o8Xpj9fIbtdZ7qUzXBkJvAkQ6p0d219xM"

if app.config["TYPE"] == 0:
    TWITTER_USER = 18
elif app.config["TYPE"] == 1:
    TWITTER_USER = 1508


######################
## PUSH CERTIFICATE ##
######################
DEV_CERT = "/pushCertificates/dev/PushDevMomentCert.pem"
DEV_KEY = "/pushCertificates/dev/PushDevMomentKey.pem"
PROD_CERT = "/pushCertificates/prod/MomentCert.pem"
PROD_KEY = "/pushCertificates/prod/MomentKey.pem"

if app.config["TYPE"] == 1:
    CERT_PUSH = PROD_CERT
    KEY_PUSH = PROD_KEY
    SANDBOX = False
else:
    CERT_PUSH = DEV_CERT
    KEY_PUSH = DEV_KEY
    SANDBOX = True


#####################
### BIG MOUSTACHE ###
#####################
if app.config["TYPE"] == 0:
    BIGMOUSTACHE_USER = 1
    BIGMOUSTACHE_MOMENT = 97
elif app.config["TYPE"] == 1:
    BIGMOUSTACHE_USER = 7477
    BIGMOUSTACHE_MOMENT = 8364


###########################
## MONTH OF THE YEAR ######
##########################
MONTH_YEAR_FR = ["MONTH0", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Décembre"]


########################################
### Score before to be among favorites #########
########################################
FAVORITE = 2
