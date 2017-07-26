from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import login_required, logout_user

from .. import db
from .models_heuresExt import HeuresExt
from .forms import DecForm, DecFormChrome
from ..app_commun.models_commun import User, Resp, load_user
from .utils.mail import Mail
from .utils.dbmethods import DbMethods
from datetime import datetime

from .utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE

from . import main_bp


def validation(request_form, role, flash_msg, redirect_route):
    heures_ext_id = []
    for i in request_form:
        result = request_form[i]
        if result in ['0', '']:
            continue
        if i.split('-')[0] == 'motif':
            heure_ext_id = i.split('-')[1]
        else:
            heure_ext_id = i
        heure_ext = HeuresExt.query.get(heure_ext_id)
        if heure_ext.status in [-1, 2]:
            continue
        if heure_ext_id != i and request_form[heure_ext_id] == '-1':
            if heure_ext.status == 1 and role == 2:
                continue
            heure_ext.motif_rejet = result
            heure_ext.status = -1
            print('motif rejet : ', result)

        elif result in ['1', '2']:
            if result == '1' and heure_ext.status == 1:
                continue
            print("ID ConsEns : " + i + " Resultat : " + result)
            if result == '1' and role == 77:
                heure_ext.status = 2
            else:
                heure_ext.status = int(result)

        elif result == '-1' and request_form['motif-' + i] == '':
            db.session.rollback()
            flash('Vous n\'avez pas donné de motif de rejet.')
            return redirect(url_for('.' + redirect_route))
            
        if role == 2:
            heure_ext.date_validation_dept = datetime.utcnow()
        elif role == 77:
            heure_ext.date_validation_dir = datetime.utcnow()
        
        if heure_ext_id not in heures_ext_id:
            heures_ext_id.append(heure_ext_id)
        print('vas y', heure_ext.status, heure_ext.date_validation_dir, heure_ext.date_validation_dept, heure_ext.motif_rejet)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash_msg = 'Erreur se produit lors de l\'opération de la base de données.'
    else:
        if heures_ext_id:
            flash_msg = 'Modification appliquée!'
            def send_emails(heure_ext_id):
                heure_ext = HeuresExt.query.get(int(heure_ext_id))
                if role == 2:
                    Mail.resp_valid_demande(heure_ext)
                    Mail.report_demande(heure_ext)
                elif role == 77:
                    Mail.dir_valid_demande(heure_ext)
            list(map(send_emails, heures_ext_id))
        
    finally:
        if flash_msg:
            flash(flash_msg)
        return redirect(url_for('.' + redirect_route))
        

@main_bp.route('/')
def redirect_index():
    return redirect(url_for('.index'))

@main_bp.route('/index')
def index():
    return render_template('templates_heuresExt/index.html',
                           title='Home')


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
        return render_template('templates_heuresExt/historique.html',
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
        return render_template('templates_heuresExt/historique.html',
                           title='Historique',
                           msg= "Il n'y a eu aucune heures extérieures.",
                           display=True)


@main_bp.route('/validation_email/<pseudo>/<heure_ext_id>/<status>/<validator>', methods=['GET', 'POST'])
def validation_email(pseudo, heure_ext_id, status, validator):
    heure_ext = HeuresExt.query.filter_by(heure_ext_id=heure_ext_id).first()
    if heure_ext is None:
        msg = 'Cette demande n\'existe pas.'
        return render_template('templates_heuresExt/validation_email.html', 
                              title='Demande n\'existe pas',
                              heure_ext=heure_ext,
                              etat=0,
                              msg=msg)
    if heure_ext.pseudo != pseudo:
        abort(404)
    from datetime import timedelta
    if datetime.utcnow().date() > heure_ext.date_demande + timedelta(days=1):
        msg = 'Ce lien n\'est plus valable, veuillez répondre à cette demande en allant à l\'appli HeuresExt!'
        return render_template('templates_heuresExt/validation_email.html', 
                              title='Lien non-valable',
                              heure_ext=heure_ext,
                              etat=0,
                              msg=msg)
    
    old_status = heure_ext.status
    if old_status == 0 or (old_status == 1 and validator == 'direction'):
        msg = 'Modification appliquée!'
        status = int(status)
        if status == -1:
            if request.method == 'GET':
                return render_template('templates_heuresExt/validation_email.html', 
                                      title='Validation par email',
                                      heure_ext=heure_ext,
                                      etat=-1,
                                      validator=validator,
                                      msg=msg)
            heure_ext.motif_rejet = request.form['motif_rejet']

        heure_ext.status = status
        if validator == 'direction':
            heure_ext.date_validation_dir = datetime.utcnow()
        elif validator == 'dept':
            heure_ext.date_validation_dept = datetime.utcnow()

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
        else:
            if validator == 'direction':
                Mail.dir_valid_demande(heure_ext)
            elif validator == 'dept':
                Mail.resp_valid_demande(heure_ext)
                Mail.report_demande(heure_ext)
        finally:
            db.session.rollback()
            return render_template('templates_heuresExt/validation_email.html', 
                                  title='Validation par email',
                                  heure_ext=heure_ext,
                                  etat=0,
                                  msg=msg)

    msg = 'Vous avez déjà traiter cette demande!'
    return render_template('templates_heuresExt/validation_email.html', 
                          title='Validation par email',
                          heure_ext=heure_ext,
                          etat=0,
                          msg=msg)


@main_bp.route('/validation_dept', methods=['GET', 'POST'])
@main_bp.route('/validation_dept/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_dept(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'asc')
    role = User.query.filter_by(user_id=user_id).first().role
    if role >= 1:
        flash_msg = None
        if request.method == 'POST':
            validation(request.form, role, flash_msg, 'validation_dept')

        msg = "Validation département - Appliquer les modifications nécessaires"
        
        if role == 77:
            list_heures_ext_users = User.query.all()
        else:
            list_heures_ext_users = User.query.filter_by(resp_id=user_id).all()
        users_id = []
        list(map(lambda user: users_id.append(user.user_id), list_heures_ext_users))

        count_histo = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
          HeuresExt.status == 0).count()
        page_max = count_histo / HISTORIQUE_PER_PAGE + 1

        user_heures_ext = HeuresExt.query.join(
          User, HeuresExt.user_id==User.user_id).filter(
          HeuresExt.user_id.in_(users_id), HeuresExt.status == 0).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo:
            return render_template('templates_heuresExt/historique.html',
                                   title='Autorisations',
                                   user_heures_ext=user_heures_ext,
                                   page=1,
                                   template_flag='validation_dept',
                                   User=User,
                                   HeuresExt=HeuresExt,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('templates_heuresExt/historique.html',
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
        flash_msg = None
        if request.method == 'POST':
            validation(request.form, role, flash_msg, 'validation_direction')


        msg = "Validation direction - Appliquer les modifications nécessaires"

        list_heures_ext_users = User.query.all()      
        users_id = []
        list(map(lambda user: users_id.append(user.user_id), list_heures_ext_users))

        count_histo = HeuresExt.query.filter(HeuresExt.user_id.in_(users_id), 
          HeuresExt.status == 1).count()

        user_heures_ext = HeuresExt.query.join(
          User, HeuresExt.user_id==User.user_id).filter(
          HeuresExt.user_id.in_(users_id), HeuresExt.status == 1).order_by(
          sortable + " " + order).paginate(
          page, count_histo, False)

        if count_histo:
            return render_template('templates_heuresExt/historique.html',
                                   title='Autorisations',
                                   user_heures_ext=user_heures_ext,
                                   page=1,
                                   template_flag='validation_direction',
                                   User=User,
                                   HeuresExt=HeuresExt,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('templates_heuresExt/historique.html',
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

    if form.validate_on_submit():
        from datetime import timedelta
        if form.decDateDebut.data < (datetime.utcnow()+timedelta(hours=2)).date():
            form.decDateDebut.errors.append('Une date déjà passée.')
            return render_template('templates_heuresExt/dec.html',
                              title='Déclaration d\'heures extérieures',
                              form=form)
        
        user_id = session.get('user_id', None)
        try:
            heure_ext = DbMethods.dec_heures_ext(user_id, form)
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
            return redirect(url_for('.dec'))
        else:
            Mail.report_demande(heure_ext)
            return redirect(url_for('.historique'))
    
    return render_template('templates_heuresExt/dec.html',
                           title='Déclaration d\'heures extérieures',
                           form=form)
