# -*- coding: utf-8 -*-
from api import app
import os

# On créé les chemins necessaires si pas créé
if not os.path.exists("api/static/data"):
	os.mkdir("api/static/data")

if not os.path.exists("api/static/data/users"):
	os.mkdir("api/static/data/users")

if not os.path.exists("api/static/data/moments"):
	os.mkdir("api/static/data/moments")

app.run(debug=True)