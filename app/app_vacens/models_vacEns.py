from .. import db
#from .ldap import Ldap


class Vacances(db.Model):
    vacances_id = db.Column(db.Integer, primary_key=True)
    date_demande = db.Column(db.Date)
    type_demande = db.Column(db.String(12))
    date_validation_dept = db.Column(db.Date)
    date_validation_dir = db.Column(db.Date)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    nb_jour = db.Column(db.Integer)
    motif = db.Column(db.String(200))
    motif_rejet = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    status = db.Column(db.Integer)
    pseudo = db.Column(db.String(40))

    def get_id(self):
        return self.vacances_id

    def __repr__(self):
        return '<Vacances %r>' % self.vacances_id

