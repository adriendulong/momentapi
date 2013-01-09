# -*- coding: utf-8 -*-
from api import app

#In which environnement we are (Dev = 0, Prod = 1)
ENV = 0

if ENV == 0:
	SERVER_ROOT = "/Users/adriendulong/Documents/Moment/Technique/API/"
else:
	SERVER_ROOT = "http://api.appmoment.fr"

PROFILE_PATH = app.root_path+"/static/data/users/"

MOMENT_PATH = app.root_path+"/static/data/moments/"
