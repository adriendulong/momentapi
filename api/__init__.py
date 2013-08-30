from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from apns import APNs, Payload



#Class pour quand sur le serveur, car l'app est sous un dossier
class WebFactionMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = '/momentapi'
        return self.app(environ, start_response)


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.secret_key = "momentisLifefrom33" 
#app.wsgi_app = WebFactionMiddleware(app.wsgi_app)
db = SQLAlchemy(app)


#Flask Login
login_manager = LoginManager()

#login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

login_manager.init_app(app)



import api.views