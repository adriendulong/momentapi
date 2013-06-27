__author__ = 'adriendulong'

from api.models import Stat
from api import fonctions
from api import db, app
from datetime import datetime

starttime = datetime.now()

s = Stat()
db.session.add(s)
db.session.commit()

endtime = datetime.now()
delta = endtime - starttime

#People we send the report
to_dests = []
dest_adri = {
    "email" : "adrien@appmoment.fr",
    "name" : "Adrien Dulong"
}
to_dests.append(dest_adri)
dest_remi = {
    "email" : "remi@appmoment.fr",
    "name" : "Remi Bardoux"
}
to_dests.append(dest_remi)

if app.config["TYPE"] == 0:
    ENV = "DEV"
elif app.config["TYPE"] == 1:
    ENV = "PROD"

#Send the report
fonctions.send_report_stats(to_dests, delta.seconds, ENV, s.get_stats())