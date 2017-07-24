from .. import db
#from .ldap import Ldap

from . import login_manager


class HeuresExt(db.Model):
    heure_ext_id = db.Column(db.Integer, primary_key=True)
    sujet = db.Column(db.String(32))
    date_demande = db.Column(db.Date)
    date_validation_dept = db.Column(db.Date)
    date_validation_dir = db.Column(db.Date)
    date_debut = db.Column(db.Date)
    lieu = db.Column(db.String(64))
    ecole_cci = db.Column(db.Boolean, default=0)
    nb_heures = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    status = db.Column(db.Integer)
    motif_rejet = db.Column(db.String(200))
    pseudo = db.Column(db.String(40))

    def __repr__(self):
        return '<HeuresExt %r>' % self.heure_ext_id


@login_manager.user_loader
def load_user(user_id):
    from ..models_commun import User
    return User.query.get(int(user_id))