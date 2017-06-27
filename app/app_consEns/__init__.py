from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

from flask_bootstrap import Bootstrap

import os

app_consEns = Flask(__name__)

app_consEns.config.from_object('config')
db = SQLAlchemy(app_consEns)

mail = Mail(app_consEns)
bootstrap = Bootstrap(app_consEns)

login_manager = LoginManager()
login_manager.init_app(app_consEns)
login_manager.login_view = 'home_cons_bp.login'
login_manager.login_message = 'Veuillez se connecter pour accéder à cette page.'

from .views import home_cons_bp, main_cons_bp, admin_cons_bp
app_consEns.register_blueprint(home_cons_bp)
app_consEns.register_blueprint(main_cons_bp)
app_consEns.register_blueprint(admin_cons_bp)

#from .views import home, main, admin
#from . import models_consEns, forms, ldap
#from .. import models_commun

#functions for templates
def conv_sqlstr_date(sql_date):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return sql_date.strftime("%d/%m/%Y")
app_consEns.jinja_env.globals.update(conv_sqlstr_date=conv_sqlstr_date)  

def abs_str(x):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return str(abs(int(x)))
app_consEns.jinja_env.globals.update(abs_str=abs_str)


os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
