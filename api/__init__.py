from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)



app = Flask(__name__)
app.config.from_object('config')
app.secret_key = "momentisLifefrom33" 
db = SQLAlchemy(app)


#Flask Login
login_manager = LoginManager()

#login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

login_manager.setup_app(app)



import api.views