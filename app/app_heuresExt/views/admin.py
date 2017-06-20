from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint)
from flask_login import logout_user, login_required, login_user, current_user

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
            if 'add_user' in request.form:
                return redirect(url_for('.admin_add_user'))
            elif 'extraction_users' in request.form:
                with open(app_heuresExt.config['FILES'] + '/users.csv', 'w') as csvfile:
                  fieldnames = ['NOM Prenom', 'Email', 'Dept', 'Login']
                  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                  writer.writeheader() 
                  for u in list_users:
                      writer.writerow({'NOM Prenom': u.nom + ' ' + u.prenom,
                        'Email': u.email,
                        'Dept': 'EP : Dept. '+ Resp.query.filter_by(resp_id=u.resp_id).first().dept,
                        'Login': u.login})
                send_from_directory(directory=app_heuresExt.config['FILES'], filename='users.csv', as_attachment=False)
                flash("La base des utilisateurs est déjà sauvegardée!")
                return render_template('admin.html', 
                                      title="Admin",
                                      form=form)
            else:
                status = [1]
                if 'signature_direction' in request.form:
                    extrait_cci = [0, 1]
                    file_name = 'signature_direction'
                elif 'extraction_cci' in request.form:
                    extrait_cci = [1]
                    file_name = 'extraction_cci'
                elif 'extraction_hors_cci' in request.form:
                    extrait_cci = [0]
                    file_name = 'extraction_hors_cci'
                elif 'historique_totale' in request.form:
                    status = [-1, 0, 1, 2]
                    extrait_cci = [0, 1]
                    file_name = 'historique_totale'

                l,n = [],[]
                for j in list_users:
                    heures_ext_en_cours = HeuresExt.query.filter(
                        HeuresExt.user_id == j.user_id, HeuresExt.status.in_(status),
                        HeuresExt.date_debut >= datetime.utcnow().date(),
                        HeuresExt.ecole_cci.in_(extrait_cci)).all()
                    for n in heures_ext_en_cours:
                        l.append(n)
                if len(l) > 0:
                    rapport = render_template('rapport_pour_direction.html',
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
                        return render_template('admin.html', 
                                              title="Admin",
                                              form=form)
                flash("Il n'y a pas de demandes")
                return render_template('admin.html', 
                                      title="Admin",
                                      form=form)
            #else:
            #    pass
        elif request.method == 'GET':
            return render_template('admin.html', 
                                  title='Admin',
                                  form=form)
                                   
        return render_template('admin.html',
                              title='Admin',
                              form=form)
        
    else:
        return render_template('index.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )


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

        return render_template('add_user.html', 
                              title='Ajout d\'un utilisateur',
                              form=form)
    else:
        return render_template('admin_add_user.html',
                           title="Interdit",
                           msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                           display=False
                           )


