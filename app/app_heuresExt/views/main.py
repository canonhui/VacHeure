from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import login_required, logout_user

from ... import db
from ..models_heuresExt import HeuresExt
from ..forms import DecForm, DecFormChrome
from ...models_commun import User, Resp, load_user
from ..utils.mail import Mail
from ..utils.dbmethods import DbMethods
from datetime import datetime

from ..utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE

from . import main_bp

#def sub_func(role, template_flag):


@main_bp.route('/historique', methods=['GET', 'POST'])
@main_bp.route('/historique/<int:page>', methods=['GET', 'POST'])
@login_required
def historique(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_debut')
    order = request.args.get('order', 'desc')
    #valid = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}
    role = User.query.filter_by(user_id=user_id).first().role
    user = User.query.filter_by(user_id=user_id).first()
    
    count_histo = HeuresExt.query.filter(
      HeuresExt.user_id == user_id).count()
    if count_histo % HISTORIQUE_PER_PAGE == 0:
        page_max = count_histo / HISTORIQUE_PER_PAGE
    else:
        page_max = int(count_histo / HISTORIQUE_PER_PAGE) + 1
    
    user_heures_ext = HeuresExt.query.join(
      User, HeuresExt.user_id==User.user_id).filter(
      User.user_id==user_id).order_by(
      sortable + " " + order).paginate(
      page, HISTORIQUE_PER_PAGE, False)

    #    for n in v:
    #        l.append(n)

    if count_histo:
        msg = "Historique des heures extérieures"
        return render_template('historique.html',
                           title='Historique',
                           user_heures_ext=user_heures_ext,
                           page=page,
                           page_max=page_max,
                           HeuresExt=HeuresExt,
                           msg=msg,
                           valid=VALID,
                           template_flag='historique',
                           current_date=datetime.utcnow().date(),
                           display=True)
    else:
        return render_template('historique.html',
                           title='Historique',
                           msg= "Il n'y a eu aucune heures extérieures.",
                           display=True)
  

@main_bp.route('/validation_email/<pseudo>/<heure_ext_id>/<int:status>')
def validation_email(pseudo, heure_ext_id, status):
    heure_ext = HeuresExt.query.filter_by(heure_ext_id=heure_ext_id).first()
    if heure_ext is None:
        return render_template('validation_email.html', 
                              title='Demande n\'existe pas',
                              msg='Cette demande n\'existe pas')
    if heure_ext.pseudo != pseudo:
        abort(404)
    from datetime import timedelta
    if datetime.utcnow().date() > heure_ext.date_demande + timedelta(days=1):
        msg = 'Ce lien n\'est plus valable, veuillez répondre à cette demande en allant à l\'appli HeuresExt!'
        return render_template('validation_email.html', 
                              title='Lien non-valable',
                              msg=msg)
    old_status = heure_ext.status
    if old_status == 0 or (status == 2 and old_status == 1):
        user_id = heure_ext.user_id
        resp_id = User.query.filter_by(user_id=user_id).first().resp_id
        u = load_user(user_id)
        role = u.get_role()
        heure_ext.status = status
        if role == 77:
            heure_ext.date_validation_dir = datetime.utcnow()
            Mail.dir_valid_demande(u, heure_ext)
        elif role == 2:
            heure_ext.date_validation_dept = datetime.utcnow()
            Mail.resp_valid_demande(u, heure_ext)
        db.session.commit()
        return render_template('validation_email.html', 
                              title='Validation par email',
                              msg='Modification appliquée!')
    return render_template('validation_email.html', 
                          title='Validation par email',
                          msg='Vous avez déjà traiter cette demande!')


@main_bp.route('/validation_dept', methods=['GET', 'POST'])
@main_bp.route('/validation_dept/<int:page>', methods=['GET', 'POST'])
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
                print('result', result);
                if result != "0":
                    print("ID HeuresExt : " + i + " Résultat : " + result)
                    heures_ext = HeuresExt.query.filter_by(heure_ext_id=i).first()
                    u = load_user(heures_ext.user_id)
                    heures_ext.date_validation_dept = datetime.utcnow()
                    if role == 2:
                        heures_ext.status = int(result)
                        Mail.resp_valid_demande(u, heures_ext)
                    elif role == 77:
                        if result == 1:
                            heures_ext.status = 2
                        else:
                            heures_ext.status = -1
                        heures_ext.date_validation_dir = datetime.utcnow()
                        Mail.dir_valid_demande(u,heures_ext)
                    db.session.commit()          
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_dept'))
        else:
            msg = "Validation département - Appliquer les modifications nécessaires"
        
        if role == 77:
            list_heures_ext_users = User.query.all()
        else:
            list_heures_ext_users = User.query.filter_by(resp_id=user_id).all()
        users_id = []
        for j in list_heures_ext_users:
            users_id.append(j.user_id)

        count_histo = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
          HeuresExt.status == 0).count()
        page_max = count_histo / HISTORIQUE_PER_PAGE + 1

        user_heures_ext = HeuresExt.query.join(
          User, HeuresExt.user_id==User.user_id).filter(
          HeuresExt.user_id.in_(users_id), HeuresExt.status == 0).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo:
            return render_template('historique.html',
                                   title='Autorisations',
                                   user_heures_ext=user_heures_ext,
                                   page=1,
                                   template_flag='validation_dept',
                                   User=User,
                                   HeuresExt=HeuresExt,
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


@main_bp.route('/validation_direction', methods=['GET', 'POST'])
@main_bp.route('/validation_direction/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_direction(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'asc')
    role = User.query.filter_by(user_id=user_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                print('i', i)
                result = request.form[i]
                if result in ["-1", "2"]: #2: admis ou -1: refusé
                    print("ID HeuresExt : " + i + " Resultat : " + result)
                    v = HeuresExt.query.filter_by(heure_ext_id=i).first()
                    v.status = int(result)
                    v.date_validation_dir = datetime.utcnow()
                    u = load_user(v.user_id)
                    Mail.dir_valid_demande(u,v)    
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_direction'))

        else:
            msg = "Validation direction - Appliquer les modifications nécessaires"        

        list_heures_ext_users = User.query.all()      
        users_id = []
        for j in list_heures_ext_users:
            users_id.append(j.user_id)

        count_histo = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
          HeuresExt.status == 1).count()

        user_heures_ext = HeuresExt.query.join(
          User, HeuresExt.user_id==User.user_id).filter(
          HeuresExt.user_id.in_(users_id), HeuresExt.status == 1).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo:
            return render_template('historique.html',
                                   title='Autorisations',
                                   user_heures_ext=user_heures_ext,
                                   page=1,
                                   template_flag='validation_direction',
                                   User=User,
                                   HeuresExt=HeuresExt,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('historique.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de déclaration d'heures extérieures.",
                                   display=False
                                   )
    else:
        abort(401)

@main_bp.route('/dec', methods=['GET', 'POST'])
@login_required
def dec():
    browser = request.user_agent.browser
    if browser == "chrome" or browser == "chromium":
        form = DecFormChrome()
    else:
        form = DecForm()
    user_id = session.get('user_id', None)
    user = load_user(user_id)

    if form.validate_on_submit():
        import random, string
        from config import NB_CODE
        factors = string.ascii_letters + string.digits
        random.seed(datetime.now())
        pseudo = ''.join(random.sample(factors, NB_CODE))

        heure_ext = DbMethods.dec_heures_ext(user_id, pseudo, form)
        Mail.report_demande(user, heure_ext)
        #Mail.vacation_notification(user, [form.decDateDebut.data, form.decDateFin.data],
        #                           Mail.notification_type.remove_vacation)
        return redirect(url_for('.historique'))
    else:
      #flash('formulaire non validé')
        return render_template('dec.html',
                     title='Déclaration d\'heures extérieures',
                     form=form)
    
    return render_template('dec.html',
                           title='Déclaration d\'heures extérieures',
                           form=form)
