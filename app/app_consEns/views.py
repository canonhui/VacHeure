from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import login_required, logout_user

from .. import db
from .models_consEns import ConsEns
from .forms import DemandeForm, DemandeFormChrome, AdminForm
from ..app_commun.models_commun import User, Resp, load_user
from .utils.mail import Mail
from .utils.dbmethods import DbMethods
from datetime import datetime

from .utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE, FILES, APPDIR

from . import cons_ens_bp


#def sub_func(role, template_flag):

def trait_dir(request_form, flash_msg):
    cons_ens_ids = []
    for i in request_form:
        result = request_form[i]
        if result in ['0', '']:
            continue
        if i.split('-')[0] == 'motif':
            cons_ens_id = i.split('-')[1]
        else:
            cons_ens_id = i
        cons_ens = ConsEns.query.get(cons_ens_id)
        if cons_ens.status in [-1, 2]:
            continue

        if cons_ens_id != i and request_form[cons_ens_id] == '-1':
            cons_ens.motif_rejet = result
            print('motif rejet : ', result)
        elif result in ['-1', '2']:
            if request_form['motif-' + i] == '' and result == '-1':
                db.session.rollback()
                flash('Vous n\'avez pas donné de motif de rejet.')
                return redirect(url_for('.validation_direction'))
            print("ID ConsEns : " + i + " Resultat : " + result)
            cons_ens.status = int(result)
            cons_ens.date_validation_dir = datetime.utcnow()
        if cons_ens_id not in cons_ens_ids:
            cons_ens_ids.append(cons_ens_id)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash_msg = 'Erreur se produit lors de l\'opération de la base de données.'
    else:
        if cons_ens_ids:
            flash_msg = 'Modification appliquée!'
            for cons_ens_id in cons_ens_ids:
                cons_ens = ConsEns.query.get(int(cons_ens_id))
                Mail.dir_valid_demande(cons_ens)
        
    finally:
        if flash_msg:
            flash(flash_msg)
        return redirect(url_for('.validation_direction'))
    

@cons_ens_bp.route('/')
def redirect_index():
    return redirect(url_for('.index'))

@cons_ens_bp.route('/index')
def index():
    return render_template('templates_consEns/index.html',
                           title='Home')


@cons_ens_bp.route('/historique', methods=['GET', 'POST'])
@cons_ens_bp.route('/historique/<int:page>', methods=['GET', 'POST'])
@login_required
def historique(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_debut')
    order = request.args.get('order', 'desc')
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
        return render_template('templates_consEns/historique.html',
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
        return render_template('templates_consEns/historique.html',
                           title='Historique',
                           msg= "Il n'y a eu aucune conseils aux entreprises.",
                           display=True)


@cons_ens_bp.route('/validation_email/<pseudo>/<cons_ens_id>/<status>', methods=['GET', 'POST'])
def validation_email(pseudo, cons_ens_id, status):
    cons_ens = ConsEns.query.filter_by(cons_ens_id=cons_ens_id).first()
    template_dir = APPDIR + '/templates/validation_email.html'
    if cons_ens is None:
        msg = 'Cette demande n\'existe pas'
        return render_template('templates_commun/validation_email.html',
                              title='Demande n\'existe pas',
                              model_instance=cons_ens,
                              etat=0,
                              msg=msg)
    if cons_ens.pseudo != pseudo:
        abort(404)

    from datetime import timedelta
    if datetime.utcnow().date() > cons_ens.date_demande + timedelta(days=1):
        msg = 'Ce lien n\'est plus valable, veuillez répondre à cette demande en allant à l\'appli ConsEns!'
        return render_template('templates_commun/validation_email.html',
                              title='Lien non-valable',
                              model_instance=cons_ens,
                              etat=0,
                              msg=msg)
        
    old_status = cons_ens.status
    if old_status == 0:
        msg = 'Modification appliquée!'
        if status == '-1':
            if request.method == 'GET':
                return render_template('templates_commun/validation_email.html',
                                      title='Validation par email',
                                      model_instance=cons_ens,
                                      etat=-1,
                                      msg=msg)
            cons_ens.motif_rejet = request.form['motif_rejet']

        cons_ens.status = int(status)
        cons_ens.date_validation_dir = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
        else:
            Mail.dir_valid_demande(cons_ens)
        finally:
            return render_template('templates_commun/validation_email.html',
                                  title='Validation par email',
                                  model_instance=cons_ens,
                                  etat=0,
                                  msg=msg)
    return render_template('templates_commun/validation_email.html',
                          title='Validation par email',
                          model_instance=cons_ens,
                          etat=0,
                          msg='Vous avez déjà traiter cette demande!')

@cons_ens_bp.route('/validation_direction', methods=['GET', 'POST'])
@cons_ens_bp.route('/validation_direction/<int:page>', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_direction(page = 1):
    user_id = session.get("user_id", None)
    sortable = request.args.get('sortable', 'date_demande')
    order = request.args.get('order', 'asc')
    role = User.query.filter_by(user_id=user_id).first().role
    if role == 77:
        flash_msg = None
        if request.method == 'POST':
            trait_dir(request.form, flash_msg)
            
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

        msg = "Validation direction - Appliquer les modifications nécessaires"
        if count_histo:
            return render_template('templates_consEns/historique.html',
                                   title='Autorisations',
                                   user_cons_ens=user_cons_ens,
                                   page=1,
                                   template_flag='validation_direction',
                                   msg=msg,
                                   display=True)
        else:
            return render_template('templates_consEns/historique.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande pour offrir des conseils aux entreprises.",
                                   display=False
                                   )
    else:
        abort(401)

@cons_ens_bp.route('/dec', methods=['GET', 'POST'])
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
        from datetime import timedelta
        if form.deDateDebut.data < (datetime.utcnow()+timedelta(hours=2)).date():
            form.deDateDebut.errors.append('Une date déjà passée.')
            return render_template('templates_consEns/dec.html',
                        title='Demande de conseils à l\'entreprise',
                        form=form)

        try:
            cons_ens = DbMethods.demande_cons_ens(user_id, form)
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
            return redirect(url_for('.dec'))
        else:
            Mail.report_demande(cons_ens)
        return redirect(url_for('.historique'))
        

    return render_template('templates_consEns/dec.html',
                           title='Demande de conseils à l\'entreprise',
                           form=form)


@cons_ens_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    import csv
    from flask import send_from_directory
    resp_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=resp_id).first().role
    if role == 77:
        form = AdminForm()
        if request.method == 'POST' and form.validate():
            list_users = User.query.all()
            if 'signature_direction' in request.form:
                status = [0]
                file_name = 'consEns_signature_direction'
                date_filter = datetime.utcnow().date()
            else:
                status = [-1, 0, 2]
                file_name = 'historique_consEns'
                date_filter = datetime.strptime("01-02-2000", "%d-%m-%Y").date()
            l,n = [],[]
            for j in list_users:
                v = ConsEns.query.filter(ConsEns.user_id==j.user_id,
                    ConsEns.status.in_(status), ConsEns.date_debut >= date_filter).all()
                for n in v:
                    l.append(n)
            if len(l) > 0:
                rapport = render_template('templates_consEns/rapport_pour_direction.html',
                                       title='Autorisations',
                                       l=l,
                                       request_type=request.form,
                                       date_du_jour=datetime.utcnow().strftime("%d/%m/%Y"), 
                                       valid=VALID
                                       )
                try:
                    from weasyprint import HTML 
                    HTML(string=rapport).write_pdf(FILES + '/' + file_name + '.pdf', stylesheets=[APPDIR + "/static/css/print.css"])
                    return send_from_directory(directory=FILES, filename=file_name + '.pdf', as_attachment=False)
                except:    
                    with open(FILES + '/' + file_name + '.html', 'w') as htmlfile:
                        htmlfile.write(rapport)
                    return send_from_directory(directory=FILES, filename=file_name + '.html', as_attachment=False)    
            else:
                flash("Il n'y a pas de demandes")
                return render_template('templates_consEns/admin.html',
                                  title="Extraction",
                                  form=form)
        elif request.method == 'GET':
            return render_template('templates_consEns/admin.html', form=form)
                                   
        #return render_template('admin.html', form=form)
        
    else:
        abort(401)

#----- not in use ----#
@cons_ens_bp.route('/validation_dept', methods=['GET', 'POST'])
@cons_ens_bp.route('/validation_dept/<int:page>', methods=['GET', 'POST'])
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
            return render_template('templates_consEns/historique.html',
                                   title='Autorisations',
                                   user_heures_ext=user_heures_ext,
                                   page=1,
                                   template_flag='validation_dept',
                                   User=User,
                                   ConsEns=ConsEns,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('templates_consEns/historique.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande d'heures extérieures.",
                                   display=False
                                   )
    else:
        abort(401)
#----------#
