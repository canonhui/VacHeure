from . import db, login_manager
from .forms import LoginForm


#from app.ldap import Ldap


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(64), index=True, unique=True)
    nom = db.Column(db.String(64), index=True, unique=False)
    prenom = db.Column(db.String(64), index=True, unique=False)
    email = db.Column(db.String(120), index=True, unique=True)
    soldeVacs = db.Column(db.Integer, default=0)
    soldeVacsEnCours = db.Column(db.Integer, default=0) 
    resp_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    role = db.Column(db.Integer)
    heures_ext = db.relationship('HeuresExt', backref='user', lazy='dynamic')
    vacens = db.relationship('Vacances', backref='user', lazy='dynamic')
    cons_ens = db.relationship('ConsEns', backref='user', lazy='dynamic')

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

    def get_name(self):
        return self.prenom+' '+self.nom

    def get_role(self):
        return self.role

    @staticmethod
    def create_user():
       # actual_user = Ldap.connect()
        if actual_user is not None:
            user = User(
                login=LoginForm().login.data,
                nom=actual_user[0],
                prenom=actual_user[1],
                email=actual_user[2],
                resp_id=actual_user[3],
                role=actual_user[4],
                soldeVacs=0,
                soldeVacsEnCours=0
            )
            return user
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_resp(self):
        if self.resp_id >= 1:
            return True
        else:
            return False

    def __repr__(self):
        return '<User %r>' % self.user_id


# Une table ridicule
class Resp(db.Model):
    key_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dept = db.Column(db.String(64))
    resp_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from .app_heuresExt.models_heuresExt import HeuresExt
from .app_vacens.models_vacEns import Vacances
from .app_consEns.models_consEns import ConsEns