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

from .app_heuresExt import app_heuresExt
from .app_vacens import app_vacens

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
	'/heuresExt': app_heuresExt,
	'/vacens': app_vacens
	})

from . import views, models_commun, forms, ldap

os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
