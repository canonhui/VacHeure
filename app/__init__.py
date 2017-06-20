from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_bootstrap import Bootstrap

from werkzeug import DispatcherMiddleware

import os

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

#mail = Mail(app_heuresExt)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez se connecter pour accéder à cette page.'

from .app_vacens import app_vacens
from .app_heuresExt import app_heuresExt

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
	'/heuresExt': app_heuresExt,
	'/vacEns': app_vacens
	})

from . import views, models_commun, forms, ldap

os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
