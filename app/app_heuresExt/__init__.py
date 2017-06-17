from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

from flask_bootstrap import Bootstrap

import os

app_heuresExt = Flask(__name__)

app_heuresExt.config.from_object('config')
db = SQLAlchemy(app_heuresExt)

mail = Mail(app_heuresExt)
bootstrap = Bootstrap(app_heuresExt)

login_manager = LoginManager()
login_manager.init_app(app_heuresExt)


from .views import home_bp, main_bp, admin_bp
app_heuresExt.register_blueprint(home_bp)
app_heuresExt.register_blueprint(main_bp)
app_heuresExt.register_blueprint(admin_bp)

from .views import home, main, admin
from . import models_heuresExt, forms, ldap
from .. import models_commun

#functions for templates
def conv_sqlstr_date(sql_date):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return sql_date.strftime("%d/%m/%Y")
app_heuresExt.jinja_env.globals.update(conv_sqlstr_date=conv_sqlstr_date)  

def abs_str(x):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return str(abs(int(x)))
app_heuresExt.jinja_env.globals.update(abs_str=abs_str)


os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
