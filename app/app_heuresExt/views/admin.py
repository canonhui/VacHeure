from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import logout_user, login_required, login_user

from .. import app_heuresExt
from ... import db
from ...models_commun import User, Resp, load_user
from ..models_heuresExt import HeuresExt
from ..forms import LoginForm, AdminForm, AddUserForm
from ..utils.mail import Mail
from ..utils.dbmethods import DbMethods
from datetime import datetime

from ..utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE

from . import admin_bp


@admin_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    import csv
    from flask import send_from_directory
    resp_id = session.get("user_id", None)
    list_users = User.query.all()
    role = User.query.filter_by(user_id=resp_id).first().role
    if role == 77:
        form = AdminForm()
        if request.method == 'POST' and form.validate():
            status = [1]
            date_filter = datetime.utcnow().date()
            if 'signature_direction' in request.form:
                extrait_cci = [0, 1]
                file_name = 'heuresExt_signature_direction'
            elif 'extraction_cci' in request.form:
                extrait_cci = [1]
                file_name = 'extraction_cci'
            elif 'extraction_hors_cci' in request.form:
                extrait_cci = [0]
                file_name = 'extraction_hors_cci'
            elif 'historique_total' in request.form:
                status = [-1, 0, 1, 2]
                extrait_cci = [0, 1]
                file_name = 'historique_heuresExt'
                date_filter = datetime.strptime("01-01-2000", "%d-%m-%Y").date()

            l,n = [],[]
            for j in list_users:
                heures_ext_en_cours = HeuresExt.query.filter(
                    HeuresExt.user_id == j.user_id, HeuresExt.status.in_(status),
                    HeuresExt.date_debut >= date_filter,
                    HeuresExt.ecole_cci.in_(extrait_cci)).all()
                for n in heures_ext_en_cours:
                    l.append(n)
            if len(l) > 0:
                rapport = render_template('templates_heuresExt/rapport_pour_direction.html',
                                       title='Fichier déjà extrait',
                                       l=l,
                                       request_type=request.form,
                                       valid=VALID,
                                       date_du_jour=datetime.utcnow().strftime("%d/%m/%Y"), 
                                       User=User
                                       )
                try:
                    from weasyprint import HTML 
                    HTML(string=rapport).write_pdf(app_heuresExt.config['FILES'] + '/' + file_name + '.pdf', stylesheets=[app_heuresExt.config['APPDIR']+"/static/css/print.css"])
                    return send_from_directory(directory=app_heuresExt.config['FILES'], filename=file_name + '.pdf', as_attachment=False)
                except:
                    with open(app_heuresExt.config['FILES'] + '/' + file_name + '.html', 'w') as htmlfile:
                        htmlfile.write(rapport)
                    return send_from_directory(directory=app_heuresExt.config['FILES'], filename=file_name + '.html', as_attachment=False)    
                    flash("Le fichier est déjà extrait.")
                    return render_template('templates_heuresExt/admin.html', 
                                          title="Admin",
                                          form=form)
            flash("Il n'y a pas de demandes")
            return render_template('templates_heuresExt/admin.html', 
                                  title="Admin",
                                  form=form)
        #else:
            #    pass
        elif request.method == 'GET':
            return render_template('templates_heuresExt/admin.html', 
                                  title='Admin',
                                  form=form)
                                   
        #return render_template('templates_heuresExt/admin.html',
        #                      title='Admin',
        #                      form=form)
        
    else:
        abort(401)


@admin_bp.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    user_id = session.get('user_id', None)
    user = load_user(user_id)
    role = User.query.filter_by(user_id=user_id).first().role
    if role == 77:
        form = AddUserForm()

        if form.validate_on_submit():
            u = User.query.filter_by(login=form.login.data).first() # does user already exist ?

            if u is None:
                # TESTER QUE LE LOGIN EXISTE
                u = User(login=form.login.data, 
                         nom=form.nom.data,
                         prenom=form.prenom.data,
                         email=form.email.data,
                         role=int(form.role.data),
                         resp_id=Resp.query.filter_by(dept=form.dept.data).first().resp_id)
                db.session.add(u)
                db.session.commit()
                flash("L'ajout de l'utilisateur \"" + form.login.data + "\" déjà effectué avec succès!")
                return redirect(url_for('.admin'))
            
            flash("Utilisateur déjà dans la base", 'danger')        
            return redirect(url_for('.admin_add_user'))

        return render_template('templates_heuresExt/add_user.html', 
                              title='Ajout d\'un utilisateur',
                              form=form)
    else:
        abort(401)


