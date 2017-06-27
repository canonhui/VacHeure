from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import login_required, logout_user

from ... import db
from ..models_consEns import ConsEns
from ..forms import DemandeForm, DemandeFormChrome
from ...models_commun import User, Resp, load_user
from ..utils.mail import Mail
from ..utils.dbmethods import DbMethods
from datetime import datetime

from ..utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE

from . import main_cons_bp

#def sub_func(role, template_flag):


@main_cons_bp.route('/historique', methods=['GET', 'POST'])
@main_cons_bp.route('/historique/<int:page>', methods=['GET', 'POST'])
@login_required
def historique(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_debut')
    order = request.args.get('order', 'desc')
    print('page', page)
    #valid = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}
    role = User.query.filter_by(user_id=user_id).first().role
    user = User.query.filter_by(user_id=user_id).first()
    
    count_histo = ConsEns.query.filter(
      ConsEns.user_id == user_id).count()
    if count_histo % HISTORIQUE_PER_PAGE == 0:
        page_max = count_histo / HISTORIQUE_PER_PAGE
    else:
        page_max = int(count_histo / HISTORIQUE_PER_PAGE) + 1
    
    user_cons_ens = ConsEns.query.join(
      User, ConsEns.user_id==User.user_id).filter(
      User.user_id==user_id).order_by(
      sortable + " " + order).paginate(
      page, HISTORIQUE_PER_PAGE, False)

    #    for n in v:
    #        l.append(n)

    if count_histo:
        msg = "Historique des conseils aux entreprises."
        return render_template('historique.html',
                           title='Historique',
                           user_cons_ens=user_cons_ens,
                           page=page,
                           page_max=page_max,
                           msg=msg,
                           valid=VALID,
                           template_flag='historique',
                           current_date=datetime.utcnow().date(),
                           display=True)
    else:
        return render_template('historique.html',
                           title='Historique',
                           msg= "Il n'y a eu aucune conseils aux entreprises.",
                           display=True)
  

@main_cons_bp.route('/validation_email/<pseudo>/<cons_ens_id>/<int:status>')
def validation_email(pseudo, cons_ens_id, status):
    cons_ens = ConsEns.query.filter_by(cons_ens_id=cons_ens_id).first()
    if cons_ens is None:
        return render_template('validation_email.html', 
                              title='Demande n\'existe pas',
                              msg='Cette demande n\'existe pas')
    if cons_ens.pseudo != pseudo:
        abort(404)
    from datetime import timedelta
    if datetime.utcnow().date() > cons_ens.date_demande + timedelta(days=1):
        msg = 'Ce lien n\'est plus valable, veuillez répondre à cette demande en allant à l\'appli ConsEns!'
        return render_template('validation_email.html', 
                              title='Lien non-valable',
                              msg=msg)
    old_status = cons_ens.status
    if old_status == 0:
        cons_ens.status = status
        cons_ens.date_validation_dir = datetime.utcnow()
        Mail.dir_valid_demande(cons_ens)
        db.session.commit()
        return render_template('validation_email.html', 
                              title='Validation par email',
                              msg='Modification appliquée!')
    return render_template('validation_email.html', 
                          title='Validation par email',
                          msg='Vous avez déjà traiter cette demande!')


@main_cons_bp.route('/validation_dept', methods=['GET', 'POST'])
@main_cons_bp.route('/validation_dept/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_dept(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'asc')
    role = User.query.filter_by(user_id=user_id).first().role
    if role >= 1:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result != "0":
                    print("ID ConsEns : " + i + " Résultat : " + result)
                    heures_ext = ConsEns.query.filter_by(heure_ext_id=i).first()
                    u = load_user(heures_ext.user_id)
                    heures_ext.date_validation_dept = datetime.utcnow()
                    if role == 2:
                        heures_ext.status = int(result)
                        Mail.resp_valid_demande(u, heures_ext)
                    elif role == 77:
                        heures_ext.status = 2
                        heures_ext.date_validation_dir = datetime.utcnow()
                        Mail.dir_valid_demande(u,heures_ext)
                    db.session.commit()          
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_dept'))
        else:
            msg = "Validation département - Appliquer les modifications nécessaires"
        
        if role == 77:
            list_cons_ens_users = User.query.all()
        else:
            list_cons_ens_users = User.query.filter_by(resp_id=user_id).all()
        users_id = []
        for j in list_cons_ens_users:
            users_id.append(j.user_id)

        count_histo = ConsEns.query.filter(ConsEns.user_id.in_(users_id), 
          ConsEns.status == 0).count()
        page_max = count_histo / HISTORIQUE_PER_PAGE + 1

        user_heures_ext = ConsEns.query.join(
          User, ConsEns.user_id==User.user_id).filter(
          ConsEns.user_id.in_(users_id), ConsEns.status == 0).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo:
            return render_template('historique.html',
                                   title='Autorisations',
                                   user_heures_ext=user_heures_ext,
                                   page=1,
                                   template_flag='validation_dept',
                                   User=User,
                                   ConsEns=ConsEns,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('historique.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande d'heures extérieures.",
                                   display=False
                                   )
    else:
        abort(401)


@main_cons_bp.route('/validation_direction', methods=['GET', 'POST'])
@main_cons_bp.route('/validation_direction/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_direction(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'asc')
    role = User.query.filter_by(user_id=user_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result not in ["0", "1"]: #2: admis ou -1: refusé
                    print("ID ConsEns : " + i + " Resultat : " + result)
                    cons_ens = ConsEns.query.filter_by(cons_ens_id=i).first()
                    cons_ens.status = int(result)
                    cons_ens.date_validation_dir = datetime.utcnow()
                    u = load_user(cons_ens.user_id)
                    Mail.dir_valid_demande(cons_ens)    
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('.historique'))

        else:
            msg = "Validation direction - Appliquer les modifications nécessaires"        

        list_cons_ens_users = User.query.all()      
        users_id = []
        for j in list_cons_ens_users:
            users_id.append(j.user_id)

        count_histo = ConsEns.query.filter(ConsEns.user_id.in_(users_id), 
          ConsEns.status == 0).count()
        page_max = count_histo / HISTORIQUE_PER_PAGE + 1

        user_cons_ens = ConsEns.query.join(
          User, ConsEns.user_id==User.user_id).filter(
          ConsEns.user_id.in_(users_id), ConsEns.status == 0).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo:
            return render_template('historique.html',
                                   title='Autorisations',
                                   user_cons_ens=user_cons_ens,
                                   page=1,
                                   template_flag='validation_direction',
                                   msg=msg,
                                   display=True)
        else:
            return render_template('historique.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande pour offrir des conseils aux entreprises.",
                                   display=False
                                   )
    else:
        abort(401)

@main_cons_bp.route('/dec', methods=['GET', 'POST'])
@login_required
def dec():
    browser = request.user_agent.browser
    if browser == "chrome" or browser == "chromium":
        form = DemandeFormChrome()
    else:
        form = DemandeForm()
    user_id = session.get('user_id', None)
    user = load_user(user_id)

    if form.validate_on_submit():
        import random, string
        from config import NB_CODE
        factors = string.ascii_letters + string.digits
        random.seed(datetime.now())
        pseudo = ''.join(random.sample(factors, NB_CODE))

        cons_ens = DbMethods.demande_cons_ens(user_id, pseudo, form)
        Mail.report_demande(cons_ens)
        #Mail.vacation_notification(user, [form.decDateDebut.data, form.decDateFin.data],
        #                           Mail.notification_type.remove_vacation)
        return redirect(url_for('.historique'))
    else:
      #flash('formulaire non validé')
        return render_template('dec.html',
                     title='Demande de conseils à l\'entreprise',
                     form=form)
    
    return render_template('dec.html',
                           title='Demande de conseils à l\'entreprise',
                           form=form)
