from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort, current_app)
from flask_login import logout_user, login_required, login_user, current_user

from ..forms import LoginForm
from ...ldap import Ldap
from ...models_commun import User
from .. import app_heuresExt

from ..utils.nocache import nocache

from . import home_bp

@login_required
@home_bp.url_value_preprocessor
def get_user_id(endpoint, values):
    user = User.query.filter_by(user_id=values.pop('user_id')).first()
    if user is None:
        abort(404)
    if user.user_id != current_user.get_id():
        abort(401)

@home_bp.url_defaults
def add_user_id(endpoint, values):
    if 'user_id' in values or not current_user:
        return
    if current_app.url_map.is_endpoint_expecting(endpoint, 'user_id'):
        values['user_id'] = current_user.get_id()


@home_bp.route('/')
@home_bp.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@home_bp.route('/login', methods=['GET', 'POST'])
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
                login_user(u, remember=form.remember_me.data)
                session["user_id"] = u.get_id()
                session["role"] = u.role
                session['username'] = u.prenom + ' ' + u.nom
                #session['remember_me'] = form.remember_me.data
                next = request.args.get('next')
                return redirect(next or url_for('main_bp.historique'))
    if current_user.get_id() is not None:
        return redirect(url_for('main_bp.historique'))
    else:       
        return render_template('login.html',
                           title='Sign In',
                           form=form)


def after_login(resp):
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    # go to next page--that is, the page before login, or index
    return redirect(request.args.get('next') or url_for('index'))

@home_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', _external=True))


@app_heuresExt.errorhandler(401)
def unauthorized(e):
    return render_template('401.html', title="Unauthorized"), 401


@app_heuresExt.errorhandler(404)
def unauthorized(e):
    return render_template('404.html', title="Page not found"), 404
