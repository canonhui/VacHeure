from ... import db
from ..models_vacEns import Vacances
from datetime import datetime

class DbMethods:
    # annulation_vacances
    # 
    # @param user User : user reference
    # @param date_debut TYPE? : bla
    # @param date_fin TYPE? : bla
    # @param nb_jour integer : bla
    @staticmethod
    def annulation_vacances(user_id, form):
        v = Vacances(
            date_demande=datetime.utcnow(),
            type_demande = 'Annulation',            
            motif=form.annulationMotif.data,
            date_debut=form.annulationDateDebut.data,
            date_fin=form.annulationDateFin.data,
            nb_jour=form.annulationNbJours.data,
            user_id=user_id,
            status=0)
        db.session.add(v)
        db.session.commit()

    # prise_vacances
    # 
    # @param user User : user reference
    # @param date_debut TYPE? : bla
    # @param date_fin TYPE? : bla
    # @param nb_jour integer : bla
    @staticmethod
    def prise_vacances(user_id, form):
        v = Vacances(
            date_demande=datetime.utcnow(),
            type_demande = 'Report',
            date_debut=form.priseDateDebut.data,
            date_fin=form.priseDateFin.data,
            nb_jour=-form.priseNbJours.data,
            user_id=user_id,
            status=0)
        db.session.add(v)
        db.session.commit()
