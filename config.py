import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	DEBUG = False
	TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    #appmoment
    USER_DB = "adulong"
    #Jar.12626
    PASSWORD_DB = "adulong"
    NAME_DB = "appmoment"
    #Emplacement de la database
    SQLALCHEMY_DATABASE_URI = 'mysql://'+USER_DB+':'+PASSWORD_DB+'@localhost/'+NAME_DB
    TYPE = 0
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=365)
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=365)

    #SERVER_NAME = "localhost"


class ProductionConfig(Config):
    DEBUG = True
    USER_DB = "appmoment"
    PASSWORD_DB = "Jar.12626"
    NAME_DB = "appmoment"
    #Emplacement de la database
    SQLALCHEMY_DATABASE_URI = 'mysql://'+USER_DB+':'+PASSWORD_DB+'@localhost/'+NAME_DB
    TYPE = 0
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=365)
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=365)

	#SERVER_NAME = "api.appmoment.fr"

class AmazonConfig(Config):
    DEBUG = True
    USER_DB = "appmoment"
    PASSWORD_DB = "Jar.12626"
    NAME_DB = "appmoment"
    #Emplacement de la database
    SQLALCHEMY_DATABASE_URI = 'mysql://'+USER_DB+':'+PASSWORD_DB+'@apimoment-mysql.c3hcodpxa4oj.eu-west-1.rds.amazonaws.com/'+NAME_DB
    TYPE = 0
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=365)
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=365)

	#SERVER_NAME = "ec2-54-228-139-53.eu-west-1.compute.amazonaws.com"

class AmazonProdConfig(Config):
    DEBUG = True
    USER_DB = "appmoment"
    PASSWORD_DB = "Jar.12626"
    NAME_DB = "appmoment"
    #Emplacement de la database
    SQLALCHEMY_DATABASE_URI = 'mysql://'+USER_DB+':'+PASSWORD_DB+'@apimoment-prod.c3hcodpxa4oj.eu-west-1.rds.amazonaws.com/'+NAME_DB
    TYPE = 1
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=365)
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=365)