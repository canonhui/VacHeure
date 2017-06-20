from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint)
from flask_login import login_required, logout_user

from ... import db
from ..models_vacEns import Vacances
from ..forms import PriseForm, PriseFormChrome, annulationForm, annulationFormChrome
from ...models_commun import User, Resp, load_user
from ..utils.mail import Mail
from ..utils.dbmethods import DbMethods
from datetime import datetime

from ..utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE

from . import main_vac



@main_vac.route('/historique_validation_vacances')
@login_required
def historique_validation_vacances():
    resp_id = session.get("user_id", None)
    valid = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}
    role = User.query.filter_by(user_id=resp_id).first().role
    if role >= 1:
        if role == 77:
            list_vacances_users = User.query.all()
        else:
            list_vacances_users = User.query.filter_by(resp_id=resp_id).all()    
        l = []
        for j in list_vacances_users:
            v = Vacances.query.filter(Vacances.user_id == j.user_id, Vacances.status != 0).all()
            for n in v:
                l.append(n)

        if len(l) > 0:
            msg = "Historique des vacances"
        else:
            msg = "Il n'y a eu aucune vacances autorisées."
        return render_template('historique_validation_vacances.html',
                               title='Historique',
                               l=l,
                               User=User,
                               Vacances=Vacances,
                               msg=msg,
                               valid=valid,
                               display=True)
    else:
        return render_template('historique_validation_vacances.html',
                               title='Interdit',
                               User=User,
                               Vacances=Vacances,
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               valid=valid,
                               display=False)


@main_vac.route('/historique_user')
@login_required
def historique_user():
    user_id = session.get("user_id", None)
    user = load_user(user_id)
    l = []
    v = Vacances.query.filter(Vacances.user_id == user_id, Vacances.status != 77).all()
    for n in v:
        l.append(n)
    if len(l) > 0:
        msg = "Historique des vacances - " + "Solde : " + str(user.soldeVacs) + " jour(s) et " + str(user.soldeVacsEnCours) + " jour(s) en cours de validation"
    else:
        msg = "Historique vacances : il n'y a pas eu de demandes effectuées."
    valid = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}
    return render_template('historique_validation_vacances.html',
                           title='Historique',
                           l=l,
                           User=User,
                           Vacances=Vacances,
                           msg=msg,
                           valid=valid,
                           display=True)

@main_vac.route('/tmp', methods=['GET', 'POST'])
@login_required  # TODO resp
def tmp():
    return redirect(url_for('.validation_vacances'))

@main_vac.route('/validation_vacances', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_vacances():
    resp_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=resp_id).first().role
    if role >= 1:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result != "0":
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = Vacances.query.filter_by(vacances_id=i).first()
                    v.status = result
                    v.date_validation_dept = datetime.utcnow()
                    u = load_user(v.user_id)
                    if result == -1: #refusées
                        u.soldeVacsEnCours = u.soldeVacsEnCours - v.nb_jour
                    Mail.resp_valid_demande(u,v)
                    db.session.commit()          
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_vacances'))
        else:
            msg = "Validation département - Appliquer les modifications nécessaires"
        
        if role == 77:
            list_vacances_users = User.query.all()
        else:
            list_vacances_users = User.query.filter_by(resp_id=resp_id).all()
        l = []
        v = []
        for j in list_vacances_users:
            v = Vacances.query.filter_by(user_id=j.user_id, status=0).all()
            for n in v:
                l.append(n)
        if len(l) > 0:
            return render_template('validation_vacances.html',
                                   title='Autorisations',
                                   l=l,
                                   User=User,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('validation_vacances.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        return render_template('validation_vacances.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )


@main_vac.route('/validation_vacances_direction', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_vacances_direction():
    resp_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=resp_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result not in ["0", "1"]: #2: admis ou -1: refusé
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = Vacances.query.filter_by(vacances_id=i).first()
                    v.status = result
                    v.date_validation_dir = datetime.utcnow()
                    u = load_user(v.user_id)
                    u.soldeVacsEnCours = u.soldeVacsEnCours - v.nb_jour
                    if result == "2":
                        u.soldeVacs = u.soldeVacs + v.nb_jour
                    Mail.dir_valid_demande(u,v)    
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_vacances_direction'))

        else:
            msg = "Validation direction - Appliquer les modifications nécessaires"        

        list_vacances_users = User.query.all()      
        l = []
        v = []
        for j in list_vacances_users:
            v = Vacances.query.filter_by(user_id=j.user_id, status=1).all()
            for n in v:
                l.append(n)
        if len(l) > 0:

            return render_template('validation_vacances_direction.html',
                                   title='Autorisations',
                                   l=l,
                                   User=User,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('validation_vacances_direction.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        return render_template('validation_vacances_direction.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )

####
def rapport_pour_direction():
    resp_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=resp_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result not in ["0", "1"]: #2: admis ou -1: refusé
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = Vacances.query.filter_by(vacances_id=i).first()
                    v.status = result
                    v.date_validation_dir = datetime.utcnow()
                    u = load_user(v.user_id)
                    u.soldeVacsEnCours = u.soldeVacsEnCours - v.nb_jour
                    if result == "2":
                        u.soldeVacs = u.soldeVacs + v.nb_jour
                    Mail.dir_valid_demande(u,v)    
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_vacances_direction'))

        else:
            msg = "Validation direction - Appliquer les modifications nécessaires"        

        list_vacances_users = User.query.all()      
        l = []
        v = []
        for j in list_vacances_users:
            v = Vacances.query.filter_by(user_id=j.user_id, status=1).all()
            for n in v:
                l.append(n)
        if len(l) > 0:
            return render_template('rapport_pour_direction.html',
                                   title='Autorisations',
                                   l=l,
                                   User=User,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('validation_vacances_direction.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        return render_template('validation_vacances_direction.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )
####



@main_vac.route('/annulation', methods=['GET', 'POST'])
@login_required
def annulation():
    browser = request.user_agent.browser
    if browser == "chrome" or browser == "chromium":
        form = annulationFormChrome()
    else:
        form = annulationForm()
    user_id = session.get('user_id', None)
    user = load_user(user_id)
    v = Vacances.query.filter(Vacances.user_id == user_id, Vacances.status == 1).all()
    w = Vacances.query.filter(Vacances.user_id == user_id, Vacances.status == 0).all()

    '''solde_vacances = 0
    if len(v) > 0:
        for i in v:
            solde_vacances = solde_vacances + i.nb_jour

    solde_vacances_validation = solde_vacances
    if len(w) > 0:
        for j in w:
            solde_vacances_validation = solde_vacances_validation + j.nb_jour
    '''
    if form.validate_on_submit():
        d1 = form.annulationDateDebut.data
        d2 = form.annulationDateFin.data
        delta_d = (d2 - d1).days
        # print(delta_d)
        if delta_d < 0 or delta_d + 1 < int(form.annulationNbJours.data):
            flash('Problème de cohérence dans les données (nb de jours)')
            return render_template('annulation.html',
                           title='Annulation de vacances',
                           solde_vacances=user.soldeVacs, #solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, #solde_vacances_validation,
                           form=form)
        user.soldeVacsEnCours = user.soldeVacsEnCours + form.annulationNbJours.data
        DbMethods.annulation_vacances(user_id, form)
        Mail.annul_demande(user, form)
        #Mail.vacation_notification(user, [form.annulationDateDebut.data, form.annulationDateFin.data],
        #                           Mail.notification_type.add_vacation)
        return redirect(url_for('.historique_user'))
    else:
        if request.method == 'POST': # POST but not validated
            flash("Erreur quelque part", 'danger')    
    return render_template('annulation.html',
                           title='Annulation de vacances',
                           solde_vacances=user.soldeVacs, #solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, #solde_vacances_validation,
                           form=form)


@main_vac.route('/prise', methods=['GET', 'POST'])
@login_required
def prise():
    browser = request.user_agent.browser
    if browser == "chrome" or browser == "chromium":
        form = PriseFormChrome()
    else:
        form = PriseForm()
    user_id = session.get('user_id', None)
    user = load_user(user_id)
    '''v = Vacances.query.filter(Vacances.user_id == user_id, Vacances.status == 1).all()
    w = Vacances.query.filter(Vacances.user_id == user_id, Vacances.status == 0).all()

    solde_vacances = 0
    if len(v) > 0:
        for i in v:
            solde_vacances = solde_vacances + i.nb_jour

    solde_vacances_validation = solde_vacances
    if len(w) > 0:
        for j in w:
            solde_vacances_validation = solde_vacances_validation + j.nb_jour
    '''
    if form.validate_on_submit():
        d1 = form.priseDateDebut.data
        d2 = form.priseDateFin.data
        delta_d = (d2 - d1).days
        if delta_d < 0 or delta_d +1  < int(form.priseNbJours.data):
            flash('Problème de cohérence dans les données (nb de jours)')
            return render_template('prise.html',
                           title='Autorisation de vacances',
                           solde_vacances=user.soldeVacs, #solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, #solde_vacances_validation,
                           form=form)
        user.soldeVacsEnCours = user.soldeVacsEnCours - form.priseNbJours.data
        DbMethods.prise_vacances(user_id, form)
        Mail.report_demande(user, form)
        #Mail.vacation_notification(user, [form.priseDateDebut.data, form.priseDateFin.data],
        #                           Mail.notification_type.remove_vacation)
        return redirect(url_for('.historique_user'))
    else:
      # print("formulaire non validé")
      pass
    
    return render_template('prise.html',
                           title='Autorisation de vacances.',
                           solde_vacances=user.soldeVacs, #  solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, # solde_vacances_validation,
                           form=form)


@main_vac.route('/user/<user_login>', methods=['GET', 'POST'])
@login_required
def user(user_login):
    actual_user = User.query.filter_by(login=user_login).first()
    nom = actual_user.nom
    prenom = actual_user.prenom
    session['username'] = prenom + ' ' + nom
    return render_template('user.html',
                           nom=prenom + ' ' + nom)




