from flask import (redirect, render_template, session, url_for, flash, request, 
                  abort, current_app)
from flask_login import logout_user, login_required, login_user, current_user

from .. import app, db
from ..forms import LoginForm, AddUserForm, AdminForm
from ..ldap import Ldap
from ..models_commun import User, load_user, Resp
from ..app_heuresExt import main_bp

from . import main_app_bp

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

@app.route('/')
@app.route('/index')
@main_app_bp.route('/')
@main_app_bp.route('/index')
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

@main_app_bp.route('/accueil')
@login_required
def accueil():
  return render_template('accueil.html',
                            title='Accueil')

@main_app_bp.route('/admin', methods=['GET', 'POST'])
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
            return redirect(url_for('.add_user'))

        return render_template('add_user.html', 
                              title='Ajout d\'un utilisateur',
                              form=form)
    else:
        abort(401)


@main_app_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', _external=True))


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html', title="Unauthorized"), 401


@app.errorhandler(404)
def unauthorized(e):
    return render_template('404.html', title="Page not found"), 404
