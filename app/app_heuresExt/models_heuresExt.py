from .. import db, login_manager
from .forms import LoginForm
from .ldap import Ldap
from ..models_commun import User
from . import login_manager


class HeuresExt(db.Model):
    heures_ext_id = db.Column(db.Integer, primary_key=True)
    date_demande = db.Column(db.Date)
    date_validation_dept = db.Column(db.Date)
    date_validation_dir = db.Column(db.Date)
    date_debut = db.Column(db.Date)
    lieu = db.Column(db.String(64))
    ecole_cci = db.Column(db.Boolean, default=0)
    nb_heures = db.Column(db.Integer)
    motif = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    status = db.Column(db.Integer)

    def __repr__(self):
        return '<HeuresExt %r>' % self.heures_ext_id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))