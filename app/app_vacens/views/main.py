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


def validation(request_form, role, redirect_route):
    vacs_ens_id = []
    flash_msg = None
    for i in request_form:
        result = request_form[i]
        if result in ['0', '']:
            continue
        if i.split('-')[0] == 'motif':
            vac_ens_id = i.split('-')[1]
        else:
            vac_ens_id = i
        vac_ens = Vacances.query.get(vac_ens_id)
        if vac_ens.status in[-1, 2]:
            continue
        user = load_user(vac_ens.user_id)

        if vac_ens_id != i and request_form[vac_ens_id] == '-1':
            if vac_ens.status == 1 and role == 2:
                continue
            vac_ens.motif_rejet = result
            vac_ens.status = -1
            user.soldeVacsEnCours = user.soldeVacsEnCours - vac_ens.nb_jour
            print('motif rejet : ', result)


        elif result in ['1', '2']:
            if result == '1' and vac_ens.status == 1:
                continue
            print("ID ConsEns : " + i + " Resultat : " + result)
            if result == '1' and role == 77:
                vac_ens.status = 2
            else:
                vac_ens.status = int(result)
            if vac_ens.status == 2:
                if vac_ens.type_demande == 'Report':
                    vac_ens.user.soldeVacs = vac_ens.user.soldeVacs + vac_ens.nb_jour
                else:
                    vac_ens.user.soldeVacs = vac_ens.user.soldeVacs - vac_ens.nb_jour
                user.soldeVacsEnCours = user.soldeVacsEnCours - vac_ens.nb_jour

        elif result == '-1' and request_form['motif-' + i] == '':
            db.session.rollback()
            flash('Vous n\'avez pas donné de motif de rejet.')
            return redirect(url_for('.' + redirect_route))
            
        if role == 2:
            vac_ens.date_validation_dept = datetime.utcnow()
        elif role == 77:
            vac_ens.date_validation_dir = datetime.utcnow()

        if vac_ens_id not in vacs_ens_id:
            vacs_ens_id.append(vac_ens_id)
        print('vas y', vac_ens.status, vac_ens.date_validation_dir, vac_ens.date_validation_dept, vac_ens.motif_rejet)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash_msg = 'Erreur se produit lors de l\'opération de la base de données.'
    else:
        if vacs_ens_id:
            flash_msg = 'Modification appliquée!'
            for vac_ens_id in vacs_ens_id:
                vac_ens = Vacances.query.get(int(vac_ens_id))
                if role == 2:
                    Mail.resp_valid_demande(vac_ens)
                    Mail.vacs_demande(vac_ens)
                elif role == 77:
                    Mail.dir_valid_demande(vac_ens)
        
    finally:
        db.session.rollback()
        if flash_msg:
            flash(flash_msg)
        return redirect(url_for('.' + redirect_route))


@main_vac.route('/validation_email/<pseudo>/<vacances_id>/<status>/<validator>', methods=['GET', 'POST'])
def validation_email(pseudo, vacances_id, status, validator):
    vac_ens = Vacances.query.filter_by(vacances_id=vacances_id).first()
    if vac_ens is None:
        msg = 'Cette demande n\'existe pas.'
        return render_template('validation_email.html', 
                              title='Demande n\'existe pas',
                              vac_ens=vac_ens,
                              etat=0,
                              msg=msg)
    if vac_ens.pseudo != pseudo:
        abort(404)
    from datetime import timedelta
    if datetime.utcnow().date() > vac_ens.date_demande + timedelta(days=1):
        msg = 'Ce lien n\'est plus valable, veuillez répondre à cette demande en allant à l\'appli VacEns!'
        return render_template('validation_email.html', 
                              title='Lien non-valable',
                              vac_ens=vac_ens,
                              etat=0,
                              msg=msg)
    
    old_status = vac_ens.status
    print(old_status, validator)
    if old_status == 0 or (old_status == 1 and validator == 'direction'):
        msg = 'Modification appliquée!'
        status = int(status)
        if status == -1:
            if request.method == 'GET':
                return render_template('validation_email.html', 
                                      title='Validation par email',
                                      vac_ens=vac_ens,
                                      etat=-1,
                                      validator=validator,
                                      msg=msg)
            vac_ens.motif_rejet = request.form['motif_rejet']
            vac_ens.user.soldeVacsEnCours = vac_ens.user.soldeVacsEnCours - vac_ens.nb_jour

        vac_ens.status = status
        if validator == 'direction':
            vac_ens.date_validation_dir = datetime.utcnow()
            if status == 2:
                if vac_ens.type_demande == 'Report':
                    vac_ens.user.soldeVacs = vac_ens.user.soldeVacs + vac_ens.nb_jour
                else:
                    vac_ens.user.soldeVacs = vac_ens.user.soldeVacs - vac_ens.nb_jour
                vac_ens.user.soldeVacsEnCours = vac_ens.user.soldeVacsEnCours - vac_ens.nb_jour
        elif validator == 'dept':
            vac_ens.date_validation_dept = datetime.utcnow()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
        else:
            if validator == 'direction':
                Mail.dir_valid_demande(vac_ens)
            elif validator == 'dept':
                Mail.resp_valid_demande(vac_ens)
                Mail.vacs_demande(vac_ens)
        finally:
            db.session.rollback()
            return render_template('validation_email.html', 
                                  title='Validation par email',
                                  vac_ens=vac_ens,
                                  etat=0,
                                  msg=msg)

    msg = 'Vous avez déjà traiter cette demande!'
    return render_template('validation_email.html', 
                          title='Validation par email',
                          vac_ens=vac_ens,
                          etat=0,
                          msg=msg)


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
            validation(request.form, role, 'validation_vacances_responsable')


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
            validation(request.form, role, 'validation_vacances_direction')


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

    if form.validate_on_submit():
        from datetime import timedelta
        d1 = form.annulationDateDebut.data
        d2 = form.annulationDateFin.data
        delta_d = (d2 - d1).days
        if delta_d <= 0 or delta_d +1 < int(form.annulationNbJours.data) or d1 < (datetime.utcnow()+timedelta(hours=2)).date():
            #flash('Problème de cohérence dans les données.')
            if d1 < (datetime.utcnow()+timedelta(hours=2)).date():
                form.annulationDateDebut.errors.append('Une date déjà passée.')
            elif delta_d <= 0:
                form.annulationDateFin.errors.append('Date de fin précède date de début.')
            else:
                form.annulationNbJours.errors.append('Nombre de jours trop grand.')
            #flash('Problème de cohérence dans les données (nb de jours)')
            return render_template('annulation.html',
                               title='Annulation de vacances',
                               solde_vacances=user.soldeVacs,
                               solde_vacances_validation=user.soldeVacsEnCours,
                               form=form)

        user.soldeVacsEnCours = user.soldeVacsEnCours + form.annulationNbJours.data
        try:
            vac_ens = DbMethods.annulation_vacances(user_id, form)
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
            return redirect(url_for('.annulation'))
        else:
            Mail.vacs_demande(vac_ens)
            return redirect(url_for('.historique_user'))

    return render_template('annulation.html',
                           title='Annulation de vacances',
                           solde_vacances=user.soldeVacs,
                           solde_vacances_validation=user.soldeVacsEnCours,
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

    if form.validate_on_submit():
        from datetime import timedelta
        d1 = form.priseDateDebut.data
        d2 = form.priseDateFin.data
        delta_d = (d2 - d1).days
        if delta_d <= 0 or delta_d +1  < int(form.priseNbJours.data) or d1 < (datetime.utcnow()+timedelta(hours=2)).date():
            if d1 < (datetime.utcnow()+timedelta(hours=2)).date():
                form.priseDateDebut.errors.append('Une date déjà passée.')
            elif delta_d <= 0:
                form.priseDateFin.errors.append('Date de fin précède date de début.')
            else:
                form.priseNbJours.errors.append('Nombre de jours trop grand.')
            return render_template('prise.html',
                               title='Autorisation de vacances.',
                               solde_vacances=user.soldeVacs,
                               solde_vacances_validation=user.soldeVacsEnCours,
                               form=form)
        
        user.soldeVacsEnCours = user.soldeVacsEnCours + int(form.priseNbJours.data)
        try:
            vac_ens = DbMethods.prise_vacances(user_id, form)
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
            return redirect(url_for('.prise'))
        else:
            Mail.vacs_demande(vac_ens)
            return redirect(url_for('.historique_user'))
        

    return render_template('prise.html',
                           title='Autorisation de vacances.',
                           solde_vacances=user.soldeVacs,
                           solde_vacances_validation=user.soldeVacsEnCours,
                           form=form)
