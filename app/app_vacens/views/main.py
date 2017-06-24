from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
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



@main_vac.route('/historique_validation_vacances', methods=['GET', 'POST'])
@main_vac.route('/historique_validation_vacances/<int:page>', methods=['GET', 'POST'])
@login_required
def historique_validation_vacances(page=1):
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'desc')
    user_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=user_id).first().role
    print(sortable, order)

    if role >= 2:
        if role == 77:
            list_vacances_users = User.query.all()
        else:
            list_vacances_users = User.query.filter_by(resp_id=user_id).all()    
        users_id = []
        for j in list_vacances_users:
            users_id.append(j.user_id)

        count_histo = Vacances.query.filter(
          Vacances.user_id.in_(users_id)).count()
        if count_histo % HISTORIQUE_PER_PAGE == 0:
            page_max = count_histo / HISTORIQUE_PER_PAGE
        else:
            page_max = int(count_histo / HISTORIQUE_PER_PAGE) + 1
        
        user_vacs_ens = Vacances.query.join(
          User, Vacances.user_id==User.user_id).filter(
          User.user_id.in_(users_id)).order_by(
          sortable + " " + order).paginate(
          page, HISTORIQUE_PER_PAGE, False)

        if count_histo > 0:
            msg = "Historique des vacances"
        else:
            msg = "Il n'y a eu aucune vacances autorisées."
        return render_template('affiche_table.html',
                               title='Historique',
                               user_vacs_ens=user_vacs_ens,
                               User=User,
                               Vacances=Vacances,
                               page=page,
                               page_max=page_max,
                               template_flag='historique_validation_vacances',
                               msg=msg,
                               valid=VALID,
                               current_date=datetime.utcnow().date(),
                               display=True)
    else:
        abort(401)


@main_vac.route('/historique_user', methods=['GET', 'POST'])
@main_vac.route('/historique_user/<int:page>', methods=['GET', 'POST'])
@login_required
def historique_user(page=1):
    sortable = request.args.get('sortable', 'date_debut')
    order = request.args.get('order', 'desc')
    user_id = session.get("user_id", None)
    user = load_user(user_id)

    count_histo = Vacances.query.filter(
      Vacances.user_id == user_id).count()
    if count_histo % HISTORIQUE_PER_PAGE == 0:
        page_max = count_histo / HISTORIQUE_PER_PAGE
    else:
        page_max = int(count_histo / HISTORIQUE_PER_PAGE) + 1
    
    user_vacs_ens = Vacances.query.join(
      User, Vacances.user_id==User.user_id).filter(
      User.user_id==user_id).order_by(
      sortable + " " + order).paginate(
      page, HISTORIQUE_PER_PAGE, False)

    if count_histo > 0:
        msg = "Historique des vacances - " + "Solde : " + str(user.soldeVacs) + " jour(s) et " + str(user.soldeVacsEnCours) + " jour(s) en cours de validation"
    else:
        msg = "Historique vacances : il n'y a pas eu de demandes effectuées."
    return render_template('affiche_table.html',
                           title='Historique',
                           user_vacs_ens=user_vacs_ens,
                           User=User,
                           Vacances=Vacances,
                           page=page,
                           page_max=page_max,
                           template_flag='historique_user',
                           msg=msg,
                           valid=VALID,
                           current_date=datetime.utcnow().date(),
                           display=True)

@main_vac.route('/validation_vacances_responsable', methods=['GET', 'POST'])
@main_vac.route('/validation_vacances_responsable/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_vacances_responsable(page=1):
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'asc')
    user_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=user_id).first().role
    if role >= 2:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result != "0":
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = Vacances.query.filter_by(vacances_id=i).first()
                    u = load_user(v.user_id)
                    if result == '-1': #refusées
                        u.soldeVacsEnCours = u.soldeVacsEnCours - v.nb_jour
                    v.date_validation_dept = datetime.utcnow()
                    if role == 2:
                        v.status = int(result)
                        Mail.resp_valid_demande(u,v)
                    else:
                        v.status = 2
                        v.date_validation_dir = datetime.utcnow()
                        Mail.dir_valid_demande(u,v)
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_vacances_responsable'))
        else:
            msg = "Validation département - Appliquer les modifications nécessaires"
        
        if role == 77:
            list_vacances_users = User.query.all()
        else:
            list_vacances_users = User.query.filter_by(resp_id=user_id).all()
        users_id = []
        for j in list_vacances_users:
            users_id.append(j.user_id)

        count_histo = Vacances.query.filter(
          Vacances.user_id.in_(users_id), Vacances.status==0).count()
        
        user_vacs_ens = Vacances.query.join(
          User, Vacances.user_id==User.user_id).filter(
          User.user_id.in_(users_id), Vacances.status==0).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo > 0:
            return render_template('affiche_table.html',
                                   title='Autorisations',
                                   user_vacs_ens=user_vacs_ens,
                                   page=1,
                                   User=User,
                                   template_flag='validation_vacances_responsable',
                                   msg=msg,
                                   valid=VALID,
                                   display=True)
        else:
            return render_template('affiche_table.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        abort(401)


@main_vac.route('/validation_vacances_direction', methods=['GET', 'POST'])
@main_vac.route('/validation_vacances_direction/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_vacances_direction(page=1):
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'asc')
    user_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=user_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result not in ["0", "1"]: #2: admis ou -1: refusé
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = Vacances.query.filter_by(vacances_id=i).first()
                    v.status = int(result)
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
        users_id = []
        for j in list_vacances_users:
            users_id.append(j.user_id)

        count_histo = Vacances.query.filter(
          Vacances.user_id.in_(users_id), Vacances.status==1).count()
        
        user_vacs_ens = Vacances.query.join(
          User, Vacances.user_id==User.user_id).filter(
          User.user_id.in_(users_id), Vacances.status==1).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo > 0:
            return render_template('affiche_table.html',
                                   title='Autorisations',
                                   user_vacs_ens=user_vacs_ens,
                                   User=User,
                                   page=1,
                                   template_flag='validation_vacances_direction',
                                   msg=msg,
                                   valid=VALID,
                                   display=True)
        else:
            return render_template('affiche_table.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        abort(401)

####
def rapport_pour_direction():
    user_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=user_id).first().role
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
