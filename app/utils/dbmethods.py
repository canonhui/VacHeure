from app import db
from app.models import HeuresExt
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
    def prise_heures_ext(user_id, form):
        v = HeuresExt(
            date_demande=datetime.utcnow(),
            type_demande = 'prise',
            date_debut=form.priseDateDebut.data,
            lieu=form.priseLieu.data,
            ecole_cci=bool(int(form.priseEcoleCCI.data)),
            nb_heures=form.priseNbHeures.data,
            user_id=user_id,
            status=0)
        db.session.add(v)
        db.session.commit()
