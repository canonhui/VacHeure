from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import logout_user, login_required, login_user, current_user

from ..forms import LoginForm
from ...ldap import Ldap
from ...models_commun import User
from .. import app_consEns

from ..utils.nocache import nocache

from . import home_cons_bp


@home_cons_bp.route('/')
@home_cons_bp.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@home_cons_bp.route('/login', methods=['GET', 'POST'])
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

@home_cons_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', _external=True))


@app_consEns.errorhandler(401)
def unauthorized(e):
    return render_template('401.html', title="Unauthorized"), 401


@app_consEns.errorhandler(404)
def unauthorized(e):
    return render_template('404.html', title="Page not found"), 404
