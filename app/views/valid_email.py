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
from config import APPDIR

from . import valid_email_bp

@valid_email_bp.route('/validation_email/<app>/<pseudo>/<cons_ens_id>/<status>', methods=['GET', 'POST'])
def validation_email(app, pseudo, cons_ens_id, status):
    cons_ens = ConsEns.query.filter_by(cons_ens_id=cons_ens_id).first()
    if cons_ens is None:
        msg = 'Cette demande n\'existe pas'
        return render_template('validation_email.html',
                              title='Demande n\'existe pas',
                              model_instance=cons_ens,
                              etat=0,
                              msg=msg)
    if cons_ens.pseudo != pseudo:
        abort(404)

    from datetime import timedelta, datetime
    if datetime.utcnow().date() > cons_ens.date_demande + timedelta(days=1):
        msg = 'Ce lien n\'est plus valable, veuillez répondre à cette demande en allant à l\'appli ConsEns!'
        return render_template('validation_email.html',
                              title='Lien non-valable',
                              model_instance=cons_ens,
                              etat=0,
                              msg=msg)
        
    old_status = cons_ens.status
    if old_status == 0:
        msg = 'Modification appliquée!'
        if status == '-1':
            if request.method == 'GET':
                return render_template('validation_email.html',
                                      title='Validation par email',
                                      model_instance=cons_ens,
                                      etat=-1,
                                      msg=msg)
            cons_ens.motif_rejet = request.form['motif_rejet']

        cons_ens.status = int(status)
        cons_ens.date_validation_dir = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            msg = 'Erreur se produit lors de l\'opération de la base de données.'
        else:
            from ..app_consEns.utils.mail import Mail
            Mail.dir_valid_demande(cons_ens)
        finally:
            return render_template('validation_email.html',
                                  title='Validation par email',
                                  model_instance=cons_ens,
                                  etat=0,
                                  msg=msg)
    return render_template('validation_email.html',
                          title='Validation par email',
                          model_instance=cons_ens,
                          etat=0,
                          msg='Vous avez déjà traiter cette demande!')
