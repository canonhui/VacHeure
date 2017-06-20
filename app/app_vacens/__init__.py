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
login_manager.login_view = 'home_vac.login'
login_manager.login_message = 'Veuillez se connecter pour accéder à cette page.'


from .views import home_vac, main_vac, admin_vac
app_vacens.register_blueprint(home_vac)
app_vacens.register_blueprint(main_vac)
app_vacens.register_blueprint(admin_vac)


#from . import models_vacEns, forms
#from .. import models_commun
#from .views import home, main, admin


def conv_sqlstr_date(sql_date):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return sql_date.strftime("%d/%m/%Y")
app_vacens.jinja_env.globals.update(conv_sqlstr_date=conv_sqlstr_date)  

def abs_str(x):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return str(abs(int(x)))
app_vacens.jinja_env.globals.update(abs_str=abs_str)


os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
