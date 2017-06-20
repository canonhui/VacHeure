from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from .. import mail
from ...models_commun import User
from enum import Enum
from config import MAIL_USERNAME, MAIL_DEFAULT_SENDER


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
    def annul_demande(user,form):
        responsable = User.query.get(user.resp_id)
        mail_object = "[HeuresExt] Demande d'annulation de vacances ("+ user.nom + " " + user.prenom +")"
        template_base_name = "mails/"
        template = template_base_name + "annul_vacs"
        #to = ['jf.bercher@esiee.fr'] #[responsable.email]
        to = [MAIL_USERNAME]
        cc = []#['abdul.alhazreb@gmail.com']  #[user.email, doyen@esiee.fr]    
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   form=form
            )

    @staticmethod
    def report_demande(user, form, heure_ext_id):
        responsable = User.query.get(user.resp_id)
        mail_object = "[HeuresExt] Demande d'une déclaration d'heures extérieures ("+ user.nom + " " + user.prenom +")"
        template_base_name = "mails/"
        template = template_base_name + "report_heures_ext"
        #to = ['jf.bercher@esiee.fr'] #[responsable.email]
        to = [MAIL_USERNAME]
        cc = []#['abdul.alhazreb@gmail.com'] #[user.email, doyen@esiee.fr]        
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   heure_ext_id=heure_ext_id,
                   form=form
            )
    @staticmethod
    def resp_valid_demande(user, validator, heures_ext):
        #responsable = User.query.get(user.resp_id)
        mail_object = "[HeuresExt] Retour sur votre déclaration d'heures extérieures"
        template_base_name = "mails/"
        template = template_base_name + "valid_heures_ext_resp"
        #to = ['jf.bercher@esiee.fr'] #[user.email]
        to = [MAIL_USERNAME]
        cc = [] # doyen ?
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   validator=validator,
                   heures_ext = heures_ext
            )

    @staticmethod
    def dir_valid_demande(user, heures_ext):
        responsable = User.query.get(user.resp_id)
        mail_object = "[HeuresExt] Retour sur votre déclaration d'heures extérieures"
        template_base_name = "mails/"
        template = template_base_name + "valid_heures_ext_dir"
        #to = ['jf.bercher@esiee.fr'] #[user.email]
        to = [MAIL_USERNAME]
        cc = [] # [doyen@esiee.fr, responsable.email]
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   heures_ext = heures_ext
            )               

#-------------------------------------

    # send_mail
    # procedure to send mail
    #
    # @param subject string : mail subject
    # @param recipients [string] : array of recipients
    # @param text_body string : mail text content
    # @param html_body string : mail html content
    @staticmethod
    def old_send_mail (subject, recipients, text_body ) : #, html_body) :
        message = Message (subject, recipients = recipients)
        message.body = text_body
        #message.html = html_body

        # !!!jfb  mail.send(message)


    # ENUM TYPE notification_type
    class notification_type (Enum) :
        add_vacation        = 1,
        remove_vacation     = 2





    # vacation_notification
    # procedure to send a mail notification 
    #
    # @param user Model.User : user 
    # @param dates_start datetime.date : date of start
    # @param dates_end datetime.date : date of end
    # @param notificationType notification_type : type of mail to send
    @staticmethod
    def vacation_notification (user, dates, notificationType) :
        responsable = User.query.get(user.resp_id)
        mail_object = "[HeuresExt] "
        template_base_name = "mails/"
        
        if notificationType == Mail.notification_type.add_vacation :
            mail_object = mail_object + "Prise de congés de " + user.nom + " " + user.prenom
            template_base_name = template_base_name + "add_vacation"
        elif notificationType == Mail.notification_type.remove_vacation :
            mail_object = mail_object + "Retrait de congés de " + user.nom + " " + user.prenom
            template_base_name = template_base_name + "remove_vacation"
            
        Mail.old_send_mail (
            mail_object,
            [responsable.email],
            render_template (
                template_base_name + ".txt",
                user = user,
                responsable = responsable,
                dates = {'debut': dates[0], 'fin': dates[1]})  )#,
