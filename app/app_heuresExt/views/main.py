from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint)
from flask_login import login_required

from ... import db
from .. import app_heuresExt
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
def historique(page = 1, sortable="nb_heures"):
   # if request.form['sortable']:
   #     sortable = request.form['sortable']
    resp_id = session.get("user_id", None)
    #valid = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}
    role = User.query.filter_by(user_id=resp_id).first().role
    if role >= 1:
        if role == 77:
            list_heures_ext_users = User.query.all()
        elif role == 2:
            list_heures_ext_users = User.query.filter_by(resp_id=resp_id).all()
        else:
            list_heures_ext_users = User.query.filter_by(user_id=resp_id).all()
        users_id = []
        for j in list_heures_ext_users:
            users_id.append(j.user_id)
        count_histo = HeuresExt.query.filter(
          HeuresExt.user_id.in_(users_id)).count()
        if count_histo % HISTORIQUE_PER_PAGE == 0:
            page_max = count_histo / HISTORIQUE_PER_PAGE
        else:
            page_max = int(count_histo / HISTORIQUE_PER_PAGE) + 1

        heuresHisto = HeuresExt.query.filter(
          HeuresExt.user_id.in_(users_id)).order_by(
          sortable + " desc").paginate(
          page, HISTORIQUE_PER_PAGE, False)

        #    for n in v:
        #        l.append(n)

        if count_histo:
            msg = "Historique des heures extérieures"
            return render_template('historique.html',
                               title='Historique',
                               heuresHisto=heuresHisto,
                               page_max=page_max,
                               User=User,
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
    else:
        return render_template('historique.html',
                               title='Interdit',
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False)

@main_bp.route('/validation_dept', methods=['GET', 'POST'])
@main_bp.route('/validation_dept/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_dept(page = 1):
    resp_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=resp_id).first().role
    validator = User.query.filter_by(user_id=resp_id).first()
    if role >= 1:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result != "0":
                    print("ID HeuresExt : " + i + " Resultat : " + result)
                    heurs_ext = HeuresExt.query.filter_by(heures_ext_id=i).first()
                    heurs_ext.status = result
                    heurs_ext.date_validation_dept = datetime.utcnow()
                    u = load_user(heurs_ext.user_id)
                    #if result == -1: #refusées
                    #    u.soldeVacsEnCours = u.soldeVacsEnCours - heurs_ext.nb_jour
                    Mail.resp_valid_demande(u, validator, heurs_ext)
                    db.session.commit()          
            msg = "Modifications appliquées"
            return redirect(url_for('.validation_dept'))
        else:
            msg = "Validation département - Appliquer les modifications nécessaires"
        
        if role == 77:
            list_heures_ext_users = User.query.all()
        else:
            list_heures_ext_users = User.query.filter_by(resp_id=resp_id).all()
        users_id = []
        for j in list_heures_ext_users:
            users_id.append(j.user_id)

        count_histo = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
          HeuresExt.status == 0).count()
        page_max = count_histo / HISTORIQUE_PER_PAGE + 1

        heuresHisto = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
            HeuresExt.status == 0).order_by(
          HeuresExt.date_demande.desc()).paginate(
            page, HISTORIQUE_PER_PAGE, False)

        if count_histo:
            return render_template('historique.html',
                                   title='Autorisations',
                                   heuresHisto=heuresHisto,
                                   page_max=page_max,
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
        return render_template('historique.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )


@main_bp.route('/validation_direction', methods=['GET', 'POST'])
@main_bp.route('/validation_direction/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_direction(page = 1):
    resp_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=resp_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result not in ["0", "1"]: #2: admis ou -1: refusé
                    print("ID HeuresExt : " + i + " Resultat : " + result)
                    v = HeuresExt.query.filter_by(heures_ext_id=i).first()
                    v.status = result
                    v.date_validation_dir = datetime.utcnow()
                    u = load_user(v.user_id)
                    Mail.dir_valid_demande(u,v)    
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('.historique'))

        else:
            msg = "Validation direction - Appliquer les modifications nécessaires"        

        list_heures_ext_users = User.query.all()      
        users_id = []
        for j in list_heures_ext_users:
            users_id.append(j.user_id)

        count_histo = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
          HeuresExt.status == 1).count()
        page_max = count_histo / HISTORIQUE_PER_PAGE + 1

        heuresHisto = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
            HeuresExt.status == 1).order_by(
          HeuresExt.date_demande.desc()).paginate(
            page, HISTORIQUE_PER_PAGE, False)

        if count_histo:
            return render_template('historique.html',
                                   title='Autorisations',
                                   heuresHisto=heuresHisto,
                                   page_max=page_max,
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
        return render_template('historique.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )

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
        DbMethods.dec_heures_ext(user_id, form)
        Mail.report_demande(user, form)
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

@app_heuresExt.errorhandler(401)
def unauthorized(e):
    return render_template('401.html', title="Unauthorized"), 401


@app_heuresExt.errorhandler(404)
def unauthorized(e):
    return render_template('404.html', title="Page not found"), 404
