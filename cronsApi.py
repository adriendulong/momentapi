__author__ = 'adriendulong'
from api import app
from api import db
from api.models import User, Moment
from datetime import datetime, timedelta, date, time
from sqlalchemy import desc, asc, and_, or_


#Today time
now = datetime.now()

#Yesterday
deltaOneDay = timedelta(days=1)
yesterday = now - deltaOneDay
endDate = date(yesterday.year, yesterday.month, yesterday.day)
print endDate

momentsToNotify = Moment.query.filter(Moment.endDate==endDate).all()

for moment in momentsToNotify:
    print "Boom notif"
    moment.notify_users_to_add_photos()


