from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from ... import mail
from ...app_commun.models_commun import User
from enum import Enum
from config import MAIL_USERNAME, MAIL_DEFAULT_SENDER
from datetime import datetime


class Mail :
    @staticmethod
    def send_async_email(app, msg):
        with app.app_context():
            mail.send(msg)

    @staticmethod
    def send_email(to, subject, template, **kwargs):
        app = current_app._get_current_object()
        cc = kwargs.get('cc',[])
        msg = Message(subject, sender=MAIL_DEFAULT_SENDER, recipients=to, cc=cc)
        msg.body = render_template(template + '.txt', **kwargs)
        try:
            msg.html = render_template(template + '.html', **kwargs)
        except:
            pass
        thr = Thread(target=Mail.send_async_email, args=[app, msg])
        thr.start()
        print('email sent')
        return thr

    @staticmethod
    def send_emailmsg(to, subject, msgbody, **kwargs):
        app = current_app._get_current_object()
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=to)
        msg.body = msgbody
        thr = Thread(target=Mail.send_async_email, args=[app, msg])
        thr.start()
        return thr

    @staticmethod
    def report_demande(heure_ext):
        if heure_ext.status == 0:
            validator = User.query.get(heure_ext.user.resp_id)
        elif heure_ext.status == 1:
            validator = User.query.filter_by(role=77).first()
        mail_object = "[HeuresExt] Demande d'une déclaration d'heures extérieures ("+ heure_ext.user.nom + " " + heure_ext.user.prenom +")"
        template_base_name = "templates_heuresExt/mails/"
        template = template_base_name + "report_heures_ext"
        to = [MAIL_USERNAME]
        cc = []#['abdul.alhazreb@gmail.com'] #[user.email, doyen@esiee.fr]
        Mail.send_email(to, mail_object, template, cc=cc,
                   validator=validator,
                   heure_ext=heure_ext
            )

    @staticmethod
    def resp_valid_demande(heure_ext):
        responsable = User.query.get(heure_ext.user.resp_id)
        mail_object = "[HeuresExt] Retour sur votre déclaration d'heures extérieures"
        template_base_name = "templates_heuresExt/mails/"
        template = template_base_name + "valid_heures_ext_resp"
        to = [MAIL_USERNAME]
        cc = [] # doyen ?
        Mail.send_email(to, mail_object, template, cc=cc,
                   responsable=responsable,
                   heure_ext=heure_ext
                    )

    @staticmethod
    def dir_valid_demande(heure_ext):
        mail_object = "[HeuresExt] Retour sur votre déclaration d'heures extérieures"
        template_base_name = "templates_heuresExt/mails/"
        template = template_base_name + "valid_heures_ext_dir"
        to = [MAIL_USERNAME]
        cc = [] # [doyen@esiee.fr, responsable.email]
        Mail.send_email(to, mail_object, template, cc=cc,
                   heure_ext = heure_ext
                    )               
