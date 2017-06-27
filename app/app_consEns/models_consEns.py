from .. import db
#from .ldap import Ldap

from . import login_manager


class ConsEns(db.Model):
    cons_ens_id = db.Column(db.Integer, primary_key=True)
    intitule = db.Column(db.String(64))
    date_demande = db.Column(db.Date)
    date_validation_dir = db.Column(db.Date)
    date_debut = db.Column(db.Date)
    nom_entreprise = db.Column(db.String(64))
    adresse = db.Column(db.String(200))
    nb_jours = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    status = db.Column(db.Integer)
    pseudo = db.Column(db.String(40))

    def __repr__(self):
        return '<ConsEns %r>' % self.cons_ens_id


@login_manager.user_loader
def load_user(user_id):
    from ..models_commun import User
    return User.query.get(int(user_id))