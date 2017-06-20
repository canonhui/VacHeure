from flask import redirect, render_template, session, url_for, flash, request
from flask_login import logout_user, login_required, login_user, current_user

from . import app
from .forms import LoginForm
from .ldap import Ldap
from .models_commun import User
from .app_heuresExt import main_bp


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.get_id() is not None:
        return redirect(url_for('index'))
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
                return redirect(next or url_for('accueil'))
                #return redirect('/user/' + form.login.data)
    else:       
        return render_template('login.html',
                           title='Sign In',
                           form=form)

@app.route('/accueil')
@login_required
def accueil():
  return render_template('accueil.html',
                            title='Accueil')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', _external=True))