import os
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

class ProductionConfig(Config):
	DEBUG = True
	USER_DB = "appmoment"
	PASSWORD_DB = "Jar.12626"
	NAME_DB = "appmoment"
	#Emplacement de la database
	SQLALCHEMY_DATABASE_URI = 'mysql://'+USER_DB+':'+PASSWORD_DB+'@localhost/'+NAME_DB