from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import flash
from flask_login import logout_user, login_required, login_user, current_user

from app.app_vacens import app_vacens
from app.app_vacens import db, models
from .forms import LoginForm, annulationForm, annulationFormChrome, PriseForm, PriseFormChrome, AdminForm, AddUserForm
from .ldap import Ldap
from .models import User, Resp
from .utils.mail import Mail
from .utils.dbmethods import DbMethods
from datetime import datetime

from .utils.nocache import nocache


def conv_sqlstr_date(sql_date):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return sql_date.strftime("%d/%m/%Y")
app_vacens.jinja_env.globals.update(conv_sqlstr_date=conv_sqlstr_date)  

def abs_str(x):
    #return datetime.strptime(sql_date, "%Y-%m-%d")
    return str(abs(int(x)))
app_vacens.jinja_env.globals.update(abs_str=abs_str)


@app_vacens.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@app_vacens.route('/')
@app_vacens.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if Ldap.connect_simple():
            u = User.query.filter_by(login=form.login.data).first()
            if not u:
                flash("Login non autorisé", 'danger')
                #return redirect(url_for('index'))
            else:
                #if not u:
                #    u = User.create_user()
                #    db.session.add(u)
                #    db.session.commit()
                login_user(u)
                session["user_id"] = u.get_id()
                session["role"] = u.role
                session['username'] = u.prenom + ' ' + u.nom
                return redirect(url_for('historique_user'))
                #return redirect('/user/' + form.login.data)
    # print(current_user.get_id())      
    if current_user.get_id() is not None:
        return redirect(url_for('historique_user'))
    else:       
        return render_template('login.html',
                           title='Sign Up',
                           form=form)


@app_vacens.route('/historique_validation_vacances')
@login_required
def historique_validation_vacances():
    resp_id = session.get("user_id", None)
    valid = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}
    role = models.User.query.filter_by(user_id=resp_id).first().role
    if role >= 1:
        if role == 77:
            list_vacances_users = models.User.query.all()
        else:
            list_vacances_users = models.User.query.filter_by(resp_id=resp_id).all()    
        l = []
        for j in list_vacances_users:
            v = models.Vacances.query.filter(models.Vacances.user_id == j.user_id, models.Vacances.status != 0).all()
            for n in v:
                l.append(n)

        if len(l) > 0:
            msg = "Historique des vacances"
        else:
            msg = "Il n'y a eu aucune vacances autorisées."
        return render_template('historique_validation_vacances.html',
                               title='Historique',
                               l=l,
                               models=models,
                               msg=msg,
                               valid=valid,
                               display=True)
    else:
        return render_template('historique_validation_vacances.html',
                               title='Interdit',
                               models=models,
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               valid=valid,
                               display=False)


@app_vacens.route('/historique_user')
@login_required
def historique_user():
    user_id = session.get("user_id", None)
    user = models.load_user(user_id)
    l = []
    v = models.Vacances.query.filter(models.Vacances.user_id == user_id, models.Vacances.status != 77).all()
    for n in v:
        l.append(n)
    if len(l) > 0:
        msg = "Historique des vacances - " + "Solde : " + str(user.soldeVacs) + " jour(s) et " + str(user.soldeVacsEnCours) + " jour(s) en cours de validation"
    else:
        msg = "Historique vacances : il n'y a pas eu de demandes effectuées."
    valid = {2: "oui", 1: "en cours (ok dept)", -1: "non", 0: "en cours"}
    return render_template('historique_validation_vacances.html',
                           title='Historique',
                           l=l,
                           models=models,
                           msg=msg,
                           valid=valid,
                           display=True)

@app_vacens.route('/tmp', methods=['GET', 'POST'])
@login_required  # TODO resp
def tmp():
    return redirect(url_for('validation_vacances'))

@app_vacens.route('/validation_vacances', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_vacances():
    resp_id = session.get("user_id", None)
    role = models.User.query.filter_by(user_id=resp_id).first().role
    if role >= 1:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result != "0":
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = models.Vacances.query.filter_by(vacances_id=i).first()
                    v.status = result
                    v.date_validation_dept = datetime.utcnow()
                    u = models.load_user(v.user_id)
                    if result == -1: #refusées
                        u.soldeVacsEnCours = u.soldeVacsEnCours - v.nb_jour
                    Mail.resp_valid_demande(u,v)
                    db.session.commit()          
            msg = "Modifications appliquées"
            return redirect(url_for('validation_vacances'))
        else:
            msg = "Validation département - Appliquer les modifications nécessaires"
        
        if role == 77:
            list_vacances_users = models.User.query.all()
        else:
            list_vacances_users = models.User.query.filter_by(resp_id=resp_id).all()
        l = []
        v = []
        for j in list_vacances_users:
            v = models.Vacances.query.filter_by(user_id=j.user_id, status=0).all()
            for n in v:
                l.append(n)
        if len(l) > 0:
            return render_template('validation_vacances.html',
                                   title='Autorisations',
                                   l=l,
                                   models=models,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('validation_vacances.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        return render_template('validation_vacances.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )


@app_vacens.route('/validation_vacances_direction', methods=['GET', 'POST'])
@login_required  # TODO resp
def validation_vacances_direction():
    resp_id = session.get("user_id", None)
    role = models.User.query.filter_by(user_id=resp_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result not in ["0", "1"]: #2: admis ou -1: refusé
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = models.Vacances.query.filter_by(vacances_id=i).first()
                    v.status = result
                    v.date_validation_dir = datetime.utcnow()
                    u = models.load_user(v.user_id)
                    u.soldeVacsEnCours = u.soldeVacsEnCours - v.nb_jour
                    if result == "2":
                        u.soldeVacs = u.soldeVacs + v.nb_jour
                    Mail.dir_valid_demande(u,v)    
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('validation_vacances_direction'))

        else:
            msg = "Validation direction - Appliquer les modifications nécessaires"        

        list_vacances_users = models.User.query.all()      
        l = []
        v = []
        for j in list_vacances_users:
            v = models.Vacances.query.filter_by(user_id=j.user_id, status=1).all()
            for n in v:
                l.append(n)
        if len(l) > 0:

            return render_template('validation_vacances_direction.html',
                                   title='Autorisations',
                                   l=l,
                                   models=models,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('validation_vacances_direction.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        return render_template('validation_vacances_direction.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )

####
def rapport_pour_direction():
    resp_id = session.get("user_id", None)
    role = models.User.query.filter_by(user_id=resp_id).first().role
    if role == 77:
        if request.method == 'POST':
            for i in request.form:
                result = request.form[i]
                if result not in ["0", "1"]: #2: admis ou -1: refusé
                    print("ID Vacances : " + i + " Resultat : " + result)
                    v = models.Vacances.query.filter_by(vacances_id=i).first()
                    v.status = result
                    v.date_validation_dir = datetime.utcnow()
                    u = models.load_user(v.user_id)
                    u.soldeVacsEnCours = u.soldeVacsEnCours - v.nb_jour
                    if result == "2":
                        u.soldeVacs = u.soldeVacs + v.nb_jour
                    Mail.dir_valid_demande(u,v)    
                    db.session.commit()
            msg = "Modifications appliquées"
            return redirect(url_for('validation_vacances_direction'))

        else:
            msg = "Validation direction - Appliquer les modifications nécessaires"        

        list_vacances_users = models.User.query.all()      
        l = []
        v = []
        for j in list_vacances_users:
            v = models.Vacances.query.filter_by(user_id=j.user_id, status=1).all()
            for n in v:
                l.append(n)
        if len(l) > 0:
            return render_template('rapport_pour_direction.html',
                                   title='Autorisations',
                                   l=l,
                                   models=models,
                                   msg=msg,
                                   display=True)
        else:
            return render_template('validation_vacances_direction.html',
                                   title='Autorisations',
                                   msg="Il n'y a pas de demande de vacances.",
                                   display=False
                                   )
    else:
        return render_template('validation_vacances_direction.html',
                               title="Interdit",
                               msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                               display=False
                               )
####



@app_vacens.route('/annulation', methods=['GET', 'POST'])
@login_required
def annulation():
    browser = request.user_agent.browser
    if browser == "chrome" or browser == "chromium":
        form = annulationFormChrome()
    else:
        form = annulationForm()
    user_id = session.get('user_id', None)
    user = models.load_user(user_id)
    v = models.Vacances.query.filter(models.Vacances.user_id == user_id, models.Vacances.status == 1).all()
    w = models.Vacances.query.filter(models.Vacances.user_id == user_id, models.Vacances.status == 0).all()

    '''solde_vacances = 0
    if len(v) > 0:
        for i in v:
            solde_vacances = solde_vacances + i.nb_jour

    solde_vacances_validation = solde_vacances
    if len(w) > 0:
        for j in w:
            solde_vacances_validation = solde_vacances_validation + j.nb_jour
    '''
    if form.validate_on_submit():
        d1 = form.annulationDateDebut.data
        d2 = form.annulationDateFin.data
        delta_d = (d2 - d1).days
        # print(delta_d)
        if delta_d < 0 or delta_d + 1 < int(form.annulationNbJours.data):
            flash('Problème de cohérence dans les données (nb de jours)')
            return render_template('annulation.html',
                           title='Annulation de vacances',
                           solde_vacances=user.soldeVacs, #solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, #solde_vacances_validation,
                           form=form)
        user.soldeVacsEnCours = user.soldeVacsEnCours + form.annulationNbJours.data
        DbMethods.annulation_vacances(user_id, form)
        Mail.annul_demande(user, form)
        #Mail.vacation_notification(user, [form.annulationDateDebut.data, form.annulationDateFin.data],
        #                           Mail.notification_type.add_vacation)
        return redirect('/historique_user')
    else:
        if request.method == 'POST': # POST but not validated
            flash("Erreur quelque part", 'danger')    
    return render_template('annulation.html',
                           title='Annulation de vacances',
                           solde_vacances=user.soldeVacs, #solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, #solde_vacances_validation,
                           form=form)


@app_vacens.route('/prise', methods=['GET', 'POST'])
@login_required
def prise():
    browser = request.user_agent.browser
    if browser == "chrome" or browser == "chromium":
        form = PriseFormChrome()
    else:
        form = PriseForm()
    user_id = session.get('user_id', None)
    user = models.load_user(user_id)
    '''v = models.Vacances.query.filter(models.Vacances.user_id == user_id, models.Vacances.status == 1).all()
    w = models.Vacances.query.filter(models.Vacances.user_id == user_id, models.Vacances.status == 0).all()

    solde_vacances = 0
    if len(v) > 0:
        for i in v:
            solde_vacances = solde_vacances + i.nb_jour

    solde_vacances_validation = solde_vacances
    if len(w) > 0:
        for j in w:
            solde_vacances_validation = solde_vacances_validation + j.nb_jour
    '''
    if form.validate_on_submit():
        d1 = form.priseDateDebut.data
        d2 = form.priseDateFin.data
        delta_d = (d2 - d1).days
        if delta_d < 0 or delta_d +1  < int(form.priseNbJours.data):
            flash('Problème de cohérence dans les données (nb de jours)')
            return render_template('prise.html',
                           title='Autorisation de vacances',
                           solde_vacances=user.soldeVacs, #solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, #solde_vacances_validation,
                           form=form)
        user.soldeVacsEnCours = user.soldeVacsEnCours - form.priseNbJours.data
        DbMethods.prise_vacances(user_id, form)
        Mail.report_demande(user, form)
        #Mail.vacation_notification(user, [form.priseDateDebut.data, form.priseDateFin.data],
        #                           Mail.notification_type.remove_vacation)
        return redirect('/historique_user')
    else:
      # print("formulaire non validé")
      pass
    
    return render_template('prise.html',
                           title='Autorisation de vacances.',
                           solde_vacances=user.soldeVacs, #  solde_vacances,
                           solde_vacances_validation=user.soldeVacsEnCours, # solde_vacances_validation,
                           form=form)


@app_vacens.route('/user/<user_login>', methods=['GET', 'POST'])
@login_required
def user(user_login):
    actual_user = User.query.filter_by(login=user_login).first()
    nom = actual_user.nom
    prenom = actual_user.prenom
    session['username'] = prenom + ' ' + nom
    return render_template('user.html',
                           nom=prenom + ' ' + nom)


@app_vacens.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    import csv
    from flask import send_from_directory
    resp_id = session.get("user_id", None)
    role = models.User.query.filter_by(user_id=resp_id).first().role
    if role == 77:

        form = AdminForm()
        if request.method == 'POST' and form.validate():
            if 'add_user' in request.form:
                return redirect(url_for('admin_add_user'))
            elif 'extraction' in request.form:
                # appel fonction extraction
                list_users = models.User.query.all()
                with open(app_vacens.config['FILES'] + '/sauvegarde.csv', 'w') as csvfile:
                  fieldnames = ['NOM Prenom',  'Dept', 'login',  'soldeVacs',  'soldeVacsEnCours']
                  writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                  writer.writeheader() 
                  for u in list_users:
                      writer.writerow({'NOM Prenom': u.nom + ' ' + u.prenom,
                        'Dept': 'EP : Dept. '+ models.Resp.query.filter_by(resp_id=u.resp_id).first().dept,
                        'login': u.login,
                        'soldeVacs': u.soldeVacs,
                        'soldeVacsEnCours': u.soldeVacsEnCours})
                #flash("Fichier extrait")
                return send_from_directory(directory=app_vacens.config['FILES'], filename='sauvegarde.csv', as_attachment=True)
                return redirect(url_for('admin'))
            elif 'signature_direction' in request.form:
                # appel fonction extraction
                list_users = models.User.query.all()
                l,n = [],[]
                for j in list_users:
                    v = models.Vacances.query.filter_by(user_id=j.user_id, status=1).all()
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


@app_vacens.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    user_id = session.get('user_id', None)
    user = models.load_user(user_id)
    role = models.User.query.filter_by(user_id=user_id).first().role
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
                         resp_id=models.Resp.query.filter_by(dept=form.dept.data).first().resp_id,
                         soldeVacs=0,
                         soldeVacsEnCours=0,
                         role=1)
                db.session.add(u)
                db.session.commit()
                return redirect(url_for('admin'))
            else:
                flash("Utilisateur déjà dans la base", 'danger')
                
            return redirect(url_for('admin_add_user'))

        return render_template('add_user.html', form=form)
    else:
        return render_template('validation_vacances_direction.html',
                           title="Interdit",
                           msg="Vous n'avez pas les droits nécessaires pour accéder à cette page.",
                           display=False
                           )




@app_vacens.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app_vacens.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401


@app_vacens.errorhandler(404)
def unauthorized(e):
    return render_template('404.html'), 404
