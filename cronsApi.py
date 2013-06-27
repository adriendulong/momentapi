__author__ = 'adriendulong'
from api import app
from api import db
from api.models import User, Moment
from api import fonctions
from datetime import datetime, timedelta, date, time
from sqlalchemy import desc, asc, and_, or_


#Today time
now = datetime.now()
#Nb Moment ended yesterday
count = 0
nb_users = 0

#Yesterday
deltaOneDay = timedelta(days=1)
yesterday = now - deltaOneDay
endDate = date(yesterday.year, yesterday.month, yesterday.day)
print endDate

momentsToNotify = Moment.query.filter(Moment.endDate==endDate).all()

for moment in momentsToNotify:
    nb_users += moment.notify_users_to_add_photos()
    count += 1



#Time when we end the script
end = datetime.now()
#Time it took
spentTime = end - now


#People we send the report
to_dests = []
dest_adri = {
    "email" : "adrien@appmoment.fr",
    "name" : "Adrien Dulong"
}
to_dests.append(dest_adri)

#Send the report
fonctions.send_report_cron(to_dests, spentTime.seconds, count, nb_users)



