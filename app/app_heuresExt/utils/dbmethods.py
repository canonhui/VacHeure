from ... import db
from ..models_heuresExt import HeuresExt
from datetime import datetime

class DbMethods:
    @staticmethod
    def dec_heures_ext(user_id, form):
        import random, string
        from config import NB_CODE
        factors = string.ascii_letters + string.digits
        random.seed(datetime.now())
        pseudo = ''.join(random.sample(factors, NB_CODE))

        heure_ext = HeuresExt(
            sujet=form.decSujet.data,
            date_demande=datetime.utcnow(),
            date_debut=form.decDateDebut.data,
            lieu=form.decLieu.data,
            ecole_cci=bool(int(form.decEcoleCCI.data)),
            nb_heures=int(form.decNbHeures.data),
            user_id=user_id,
            status=0,
            pseudo=pseudo)
        db.session.add(heure_ext)
        db.session.commit()
        return heure_ext
