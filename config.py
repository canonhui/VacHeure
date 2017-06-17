import os


# global configs
basedir = os.path.abspath(os.path.dirname(__file__))


# database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True


# login token
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'


# email server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
#Pour ce faire j'ai autorisé les applications moins sécurisées pour ce compte. faudrai le fermer apres le projet.
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = MAIL_USERNAME


# global constants
FILES = basedir + '/files'
APPDIR = basedir + '/app'

VALID = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}

#pagination
HISTORIQUE_PER_PAGE = 14