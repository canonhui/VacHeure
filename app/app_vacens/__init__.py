from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

from flask_bootstrap import Bootstrap

import os

app_vacens = Flask(__name__)

app_vacens.config.from_object('config')
db = SQLAlchemy(app_vacens)

mail = Mail(app_vacens)
bootstrap = Bootstrap(app_vacens)

login_manager = LoginManager()
login_manager.init_app(app_vacens)

from app.app_vacens import views, models, forms, ldap

os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
