from ... import db
from ..models_consEns import ConsEns
from datetime import datetime

class DbMethods:
    @staticmethod
    def demande_cons_ens(user_id, pseudo, form):
        adresse = ', '.join([form.deAdrRue.data, form.deAdrCode.data, 
                form.deAdrVille.data])
        if form.deAdrInfoExtra.data:
            adresse = ', '.join([form.deAdrInfoExtra.data, adresse])
        cons_ens = ConsEns(
            sujet=form.deSujet.data,
            nom_entreprise=form.deNomEntreprise.data,
            adresse=adresse,
            date_demande=datetime.utcnow(),
            date_debut=form.deDateDebut.data,
            nb_jours=int(form.deNbJours.data),
            user_id=user_id,
            status=0,
            pseudo=pseudo)
        db.session.add(cons_ens)
        db.session.commit()
        return cons_ens

