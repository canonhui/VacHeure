from ... import db
from ..models_heuresExt import HeuresExt
from datetime import datetime

class DbMethods:
    @staticmethod
    def dec_heures_ext(user_id, form):
        v = HeuresExt(
            date_demande=datetime.utcnow(),
            date_debut=form.decDateDebut.data,
            lieu=form.decLieu.data,
            ecole_cci=bool(int(form.decEcoleCCI.data)),
            nb_heures=form.decNbHeures.data,
            user_id=user_id,
            status=0)
        db.session.add(v)
        db.session.commit()