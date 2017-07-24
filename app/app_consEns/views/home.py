from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import logout_user, login_required, login_user, current_user

from ..forms import LoginForm
from ... import db
from ...ldap import Ldap
from ...models_commun import User
from .. import app_consEns

from ..utils.nocache import nocache

from . import home_cons_bp


@home_cons_bp.route('/')
def redirect_index():
    return redirect(url_for('.index'))

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
                return redirect(next or url_for('main_cons_bp.historique'))
    if current_user.get_id() is not None:
        return redirect(url_for('main_cons_bp.historique'))
    else:       
        return render_template('login.html',
                           title='Sign In',
                           form=form)


@home_cons_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', _external=True))


@app_consEns.errorhandler(401)
def unauthorized(e):
    db.session.rollback()
    msg = 'Vous n\'avez pas le droit d\'accéder à cette page.'
    return render_template('errors.html', title="Unauthorized", msg=msg), 401


@app_consEns.errorhandler(404)
def unauthorized(e):
    db.session.rollback()
    msg = 'Cette page n\'existe pas.'
    return render_template('errors.html', title="Page not found", msg=msg), 404

@app_consEns.errorhandler(500)
def unauthorized(e):
    db.session.rollback()
    msg = 'L\'administrateur est déjà notifié, désolé pour l\'inconvénient causé.'
    return render_template('errors.html', title="Unexpected error", msg=msg), 500