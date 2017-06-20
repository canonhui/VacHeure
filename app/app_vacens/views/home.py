from flask import (redirect, render_template, request, session, url_for, flash, 
                  Blueprint, abort)
from flask_login import logout_user, login_required, login_user, current_user

from ..forms import LoginForm
from ...ldap import Ldap
from ...models_commun import User
from .. import app_vacens

from ..utils.nocache import nocache

from . import home_vac


@home_vac.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@home_vac.route('/')
@home_vac.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if Ldap.connect_simple():
            u = User.query.filter_by(login=form.login.data).first()
            if not u:
                flash("Login non autorisé", 'danger')
                #return redirect(url_for('.index'))
            else:
                #if not u:
                #    u = User.create_user()
                #    db.session.add(u)
                #    db.session.commit()
                login_user(u)
                session["user_id"] = u.get_id()
                session["role"] = u.role
                session['username'] = u.prenom + ' ' + u.nom
                return redirect(url_for('main_vac.historique_user'))
                #return redirect('/user/' + form.login.data)
    # print(current_user.get_id())      
    if current_user.get_id() is not None:
        return redirect(url_for('main_vac.historique_user'))
    else:       
        return render_template('login.html',
                           title='Sign Up',
                           form=form)


@home_vac.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app_vacens.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401


@app_vacens.errorhandler(404)
def unauthorized(e):
    return render_template('404.html'), 404
