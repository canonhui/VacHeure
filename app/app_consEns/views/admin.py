from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import logout_user, login_required, login_user

from .. import app_consEns
from ... import db
from ...models_commun import User, Resp, load_user
from ..models_consEns import ConsEns
from ..forms import LoginForm, AdminForm
from ..utils.mail import Mail
from ..utils.dbmethods import DbMethods
from datetime import datetime

from ..utils.nocache import nocache

from config import VALID, HISTORIQUE_PER_PAGE

from . import admin_cons_bp


@admin_cons_bp.route('/admin', methods=['GET', 'POST'])
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
                rapport = render_template('rapport_pour_direction.html',
                                       title='Autorisations',
                                       l=l,
                                       request_type=request.form,
                                       date_du_jour=datetime.utcnow().strftime("%d/%m/%Y"), 
                                       valid=VALID
                                       )
                try:
                    from weasyprint import HTML 
                    HTML(string=rapport).write_pdf(app_consEns.config['FILES'] + '/' + file_name + '.pdf', stylesheets=[app_consEns.config['APPDIR']+"/static/css/print.css"])
                    return send_from_directory(directory=app_consEns.config['FILES'], filename=file_name + '.pdf', as_attachment=False)
                except:    
                    with open(app_consEns.config['FILES'] + '/' + file_name + '.html', 'w') as htmlfile:
                        htmlfile.write(rapport)
                    return send_from_directory(directory=app_consEns.config['FILES'], filename=file_name + '.html', as_attachment=False)    
            else:
                flash("Il n'y a pas de demandes")
                return render_template('admin.html',
                                  title="Extraction",
                                  form=form)
        elif request.method == 'GET':
            return render_template('admin.html', form=form)
                                   
        #return render_template('admin.html', form=form)
        
    else:
        abort(401)
