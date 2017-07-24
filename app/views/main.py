from flask import (redirect, render_template, session, url_for, flash, request, 
                  abort, current_app, jsonify)
from flask_login import logout_user, login_required, login_user, current_user

from .. import app, db
from ..forms import LoginForm, AddUserForm, AdminForm
from ..ldap import Ldap
from ..models_commun import User, load_user, Resp
from ..app_heuresExt.models_heuresExt import HeuresExt
from ..app_consEns.models_consEns import ConsEns
from ..app_vacens.models_vacEns import Vacances

from . import main_app_bp
'''
@login_required
@main_app_bp.url_value_preprocessor
def get_user_id(endpoint, values):
    user = User.query.filter_by(user_id=values.pop('user_id')).first()
    if user is None:
        abort(404)
    if user.user_id != current_user.get_id():
        abort(401)

@main_app_bp.url_defaults
def add_user_id(endpoint, values):
    if 'user_id' in values or not current_user:
        return
    if current_app.url_map.is_endpoint_expecting(endpoint, 'user_id'):
        values['user_id'] = current_user.get_id()
'''

@app.route('/')
def redirect_index():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if Ldap.connect_simple():
            u = User.query.filter_by(login=form.login.data).first()
            if not u:
                flash("Login non autorisé", 'danger')
            else:
                #if not u:
                #    u = User.create_user()
                #    db.session.add(u)
                #    db.session.commit()
                print('remember me')
                login_user(u, remember=form.remember_me.data)
                #session["user_id"] = u.get_id()
                #session["role"] = u.role
                #session['username'] = u.prenom + ' ' + u.nom
                #session['remember_me'] = form.remember_me.data
                next = request.args.get('next')
                return redirect(next or url_for('main_app_bp.accueil'))
    if current_user.get_id() is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    else:       
        return render_template('login.html',
                           title='Sign In',
                           form=form)

@main_app_bp.route('/accueil/')
@login_required
def accueil():
  return render_template('accueil.html',
                            title='Accueil')

@main_app_bp.route('/admin/', methods=['GET', 'POST'])
@login_required
def admin():
    import csv
    from flask import send_from_directory
    user_id = session.get("user_id", None)
    role = User.query.filter_by(user_id=user_id).first().role

    if role == 77:
        form = AdminForm()
        if request.method == 'POST' and form.validate():
            if 'add_user' in request.form:
                return redirect(url_for('.add_user'))
            elif 'extraction_users' in request.form:
                # appel fonction extraction
                list_users = User.query.all()
                with open(app.config['FILES'] + '/utilisateurs.csv', 'w') as csvfile:
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
                send_from_directory(directory=app.config['FILES'], filename='utilisateurs.csv', as_attachment=False)
                flash("La base des utilisateurs est déjà sauvegardée!")
                return redirect(url_for('.admin'))
            else:
                bases = {'heure_ext_zero': HeuresExt, 'vac_ens_zero': Vacances, 'cons_ens_zero': ConsEns}
                for key in request.form.keys():
                    if key in bases.keys():
                        base = bases[key]
                    if key == 'vac_ens_zero':
                        User.reset_to_zero()
                base.query.delete()
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash('Erreur se produit lors de l\'opération de la base de données.')
                else:
                    flash('La base de données est remise à zéro.')
                finally:
                    return redirect(url_for('.admin'))

        elif request.method == 'GET':
            return render_template('admin.html', title='Admin', form=form)
                                   
        #return render_template('admin.html', form=form)
        
    else:
        abort(401)



@main_app_bp.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    user_id = session.get('user_id', None)
    user = load_user(user_id)
    role = User.query.filter_by(user_id=user_id).first().role
    if role == 77:
        form = AddUserForm()
        if request.method == 'GET':
            return render_template('add_user.html', 
                              title='Ajout d\'un utilisateur',
                              form=form)

        if form.validate_on_submit():
            print(request.form)
            u = User.query.filter_by(login=form.login.data).first() # does user already exist ?
            flash_msg = None
            if 'updater' in request.form:
                if u is None:
                    u = User(login=form.login.data,
                             nom=form.nom.data,
                             prenom=form.prenom.data,
                             email=form.email.data,
                             role=int(form.role.data),
                             resp_id=request.form['dept'])
                    db.session.add(u)
                    flash_msg = "L'ajout de l'utilisateur \"" + form.login.data + "\" est déjà effectué avec succès!"
                else:
                    u.nom=form.nom.data
                    u.prenom=form.prenom.data
                    u.email=form.email.data
                    u.role=int(form.role.data)
                    u.resp_id=request.form['dept']
                    flash_msg = "La mise à jour de l'utilisateur \"" + form.login.data + "\" est déjà effectué avec succès!"

            if 'supprimer' in request.form:
                if u is None:
                    flash('Utilisateur n\'existe pas!')
                    return redirect(url_for('.add_user'))
                else:
                    db.session.delete(u)
                    flash_msg = "La suppression de l'utilisateur \"" + form.login.data + "\" est déjà effectué avec succès!"

            if flash_msg:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    flash_msg = 'Erreur se produit lors de l\'opération de la base de données.'
                else:
                    flash(flash_msg)
                finally:
                    return redirect(url_for('.admin'))
            return redirect(url_for('.add_user'))

        else:
            flash('Formulaire non validé.')
            return redirect(url_for('.add_user'))
        
    else:
        abort(401)


@main_app_bp.route('/admin/edit_user')
@login_required
def edit_projet():
    login = request.args.get('login', '', str)

    print('projet id', login)
    user = User.query.filter_by(login=login).first()
    if user:
        return jsonify({'prenom': user.prenom, 'nom': user.nom, 'email': user.email, 'role': user.role, 'dept': user.resp_id})
    return jsonify({'msg': 'Ajoutez ce nouvel enseignant.'})


@main_app_bp.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', _external=True))


@app.errorhandler(401)
def unauthorized(e):
    db.session.rollback()
    msg = 'Vous n\'avez pas le droit d\'accéder à cette page.'
    return render_template('errors.html', title="Unauthorized", msg=msg), 401


@app.errorhandler(404)
def unauthorized(e):
    db.session.rollback()
    msg = 'Cette page n\'existe pas.'
    return render_template('errors.html', title="Page not found", msg=msg), 404

@app.errorhandler(500)
def unauthorized(e):
    db.session.rollback()
    msg = 'L\'administrateur est déjà notifié, désolé pour l\'inconvénient causé.'
    return render_template('errors.html', title="Unexpected error", msg=msg), 500