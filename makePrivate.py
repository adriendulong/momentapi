from api.models import User, Moment
from api import fonctions
from datetime import datetime, timedelta, date, time
from sqlalchemy import or_
from api import db

usersToChange = User.query.filter(or_(User.privacy==2, User.privacy==1)).all()

#We set to private all these users
for user in usersToChange:
    user.privacy = 0
    db.session.commit()

momentsToChange = Moment.query.filter(or_(Moment.privacy==2, Moment.privacy==1)).all()

for moment in momentsToChange:
    moment.privacy = 0
    db.session.commit()
