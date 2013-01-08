import os
basedir = os.path.abspath(os.path.dirname(__file__))

#appmoment
USER_DB = "adulong"
#Jar.12626
PASSWORD_DB = "adulong"

NAME_DB = "appmoment"


#Emplacement de la database
SQLALCHEMY_DATABASE_URI = 'mysql://'+USER_DB+':'+PASSWORD_DB+'@localhost/'+NAME_DB