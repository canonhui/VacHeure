from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint)
from flask_login import logout_user, login_required, login_user, current_user

from .. import app_vacens
from ... import db
from ...models_commun import User, Resp, load_user
from ..models_vacEns import Vacances
from ..forms import LoginForm, AdminForm, AddUserForm
from ..utils.mail import Mail
from ..utils.dbmethods import DbMethods
from datetime import datetime

from ..utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE

from . import admin_vac


@admin_vac.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    import csv
    from flask import send_from_directory
    resp_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=resp_id).first().role
    if role == 77:

        form = AdminForm()
        if request.method == 'POST' and form.validate():
            if 'add_user' in request.form:
                return redirect(url_for('.admin_add_user'))
            elif 'extraction' in request.form:
                # appel fonction extraction
                list_users = User.query.all()
                with open(app_vacens.config['FILES'] + '/sauvegarde.csv', 'w') as csvfile:
                  fieldnames = ['NOM Prenom',  'Dept', 'login',  'soldeVacs',  'soldeVacsEnCours']
                  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                  writer.writeheader() 
                  for u in list_users:
                      writer.writerow({'NOM Prenom': u.nom + ' ' + u.prenom,
                        'Dept': 'EP : Dept. '+ Resp.query.filter_by(resp_id=u.resp_id).first().dept,
                        'login': u.login,
                        'soldeVacs': u.soldeVacs,
                        'soldeVacsEnCours': u.soldeVacsEnCours})
                #flash("Fichier extrait")
                return send_from_directory(directory=app_vacens.config['FILES'], filename='sauvegarde.csv', as_attachment=True)
                return redirect(url_for('.admin'))
            elif 'signature_direction' in request.form:
                # appel fonction extraction
                list_users = User.query.all()
                l,n = [],[]
                for j in list_users:
                    v = Vacances.query.filter_by(user_id=j.user_id, status=1).all()
                    for n in v:
                        l.append(n)
                if len(l) > 0:
                    rapport = render_template('rapport_pour_direction.html',
                                           title='Autorisations',
                                           l=l,
                                           date_du_jour=datetime.utcnow().strftime("%d/%m/%Y"), 
                                           models=models
                                           )
                    try:
                        from weasyprint import HTML 
                        HTML(string=rapport).write_pdf(app_vacens.config['FILES'] + '/signature_direction.pdf', stylesheets=[app_vacens.config['APPDIR']+"/static/css/print.css"])
                        return send_from_directory(directory=app_vacens.config['FILES'], filename='signature_direction.pdf', as_attachment=True)
                    except:    
                        with open(app_vacens.config['FILES'] + '/signature_direction.html', 'w') as htmlfile:
                            htmlfile.write(rapport)
                        return send_from_directory(directory=app_vacens.config['FILES'], filename='signature_direction.html', as_attachment=True)    
            else:
                pass
        elif request.method == 'GET':
            return render_template('admin.html', form=form)
                                   
        return render_template('admin.html', form=form)
        
    else:
        return render_template('validation_vacances_direction.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )


@admin_vac.route('/admin/add_user', methods=['GET', 'POST'])
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
                         email=form.login.data + "@esiee.fr",
                         resp_id=Resp.query.filter_by(dept=form.dept.data).first().resp_id,
                         soldeVacs=0,
                         soldeVacsEnCours=0,
                         role=1)
                db.session.add(u)
                db.session.commit()
                return redirect(url_for('.admin'))
            else:
                flash("Utilisateur déjà dans la base", 'danger')
                
            return redirect(url_for('.admin_add_user'))

        return render_template('add_user.html', form=form)
    else:
        return render_template('validation_vacances_direction.html',
                           title="Interdit",
                           msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                           display=False
                           )
