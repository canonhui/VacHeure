from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from flask_bootstrap import Bootstrap

from werkzeug import DispatcherMiddleware

import os

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

mail = Mail(app)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez se connecter pour accéder à cette page.'

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    '''
    The size of log file is limited to 1Mb, and we will keep the last ten log files as backups.
    '''
    file_handler = RotatingFileHandler('tmp/vaConsHeures.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('vaConsHeures startup')

    '''
    Pour la notification des bugs avec email, on a besoin de configurer un serveur email.
    '''
    '''
    from logging.handlers import SMTPHandler
    from config import ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), MAIL_USERNAME,
        ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    '''

from .app_commun import commun_bp
from .app_vacens import vac_ens_bp
from .app_heuresExt import heures_ext_bp
from .app_consEns import cons_ens_bp

app.register_blueprint(commun_bp)
app.register_blueprint(vac_ens_bp, url_prefix='/vacEns')
app.register_blueprint(heures_ext_bp, url_prefix='/heuresExt')
app.register_blueprint(cons_ens_bp, url_prefix='/consEns')

#from . import views, models_commun, forms, ldap

#functions for templates
def conv_sqlstr_date(sql_date):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return sql_date.strftime("%d/%m/%Y")
app.jinja_env.globals.update(conv_sqlstr_date=conv_sqlstr_date)  

def abs_str(x):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return str(abs(int(x)))
app.jinja_env.globals.update(abs_str=abs_str)

os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
