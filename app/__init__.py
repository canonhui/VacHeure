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
from .app_consEns import app_consEns

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
	'/heuresExt': app_heuresExt,
	'/vacEns': app_vacens,
	'/consEns':app_consEns
	})

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
    app_heuresExt.logger.addHandler(file_handler)
    app_vacens.logger.addHandler(file_handler)
    app_consEns.logger.addHandler(file_handler)
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
    app_heuresExt.logger.addHandler(mail_handler)
    app_vacens.logger.addHandler(mail_handler)
    app_consEns.logger.addHandler(mail_handler)
    '''

from .views import main_app_bp, valid_email_bp
app.register_blueprint(main_app_bp)
app.register_blueprint(valid_email_bp)

#from . import views, models_commun, forms, ldap

os.environ["HTTP_PROXY"] = "http://cache.esiee.fr:3128"
os.environ["HTTPS_PROXY"] = "http://cache.esiee.fr:3128"
