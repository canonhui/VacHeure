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
    def report_demande(cons_ens):
        #responsable = User.query.get(user.resp_id)
        mail_object = "[ConsEns] Demande d'une déclaration de conseils à  l'entreprise ("+ cons_ens.user.nom + " " + cons_ens.user.prenom +")"
        template_base_name = "templates_consEns/mails/"
        template = template_base_name + "report_cons_ens"
        directeur = User.query.filter_by(role=77, login='wuw').first().email
        #to = [directeur]
        to = ['ptt2hui@gmail.com']
        cc = []
        Mail.send_email(to, mail_object, template, cc=cc,
                   cons_ens=cons_ens
            )

    @staticmethod
    def dir_valid_demande(cons_ens):
        mail_object = "[ConsEns] Retour sur votre déclaration de conseils à l'entreprise"
        template_base_name = "templates_consEns/mails/"
        template = template_base_name + "valid_cons_ens_dir"
        #to = [cons_ens.user.email]
        to = ['ptt2hui@gmail.com']
        cc = [] # [doyen@esiee.fr, responsable.email]
        Mail.send_email(to, mail_object, template, cc=cc,
                   cons_ens = cons_ens
            )               
