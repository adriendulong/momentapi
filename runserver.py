# -*- coding: utf-8 -*-
from api import app
import os

# On créé les chemins necessaires si pas créé
if not os.path.exists("data"):
	os.mkdir("data")

if not os.path.exists("data/users"):
	os.mkdir("data/users")

if not os.path.exists("data/moments"):
	os.mkdir("data/moments")

app.run(debug=True)