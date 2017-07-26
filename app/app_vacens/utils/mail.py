from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from ... import mail
from ...app_commun.models_commun import User
from enum import Enum
from config import MAIL_USERNAME, MAIL_DEFAULT_SENDER



class Mail :

    @staticmethod
    def send_async_email(app_vacens, msg):
        with app_vacens.app_context():
            mail.send(msg)

    @staticmethod
    def send_email(to, subject, template, **kwargs):
        app_vacens = current_app._get_current_object()
        cc = kwargs.get('cc',[])
        msg = Message(subject, sender=app_vacens.config['MAIL_USERNAME'], recipients=to, cc=cc)
        msg.body = render_template(template + '.txt', **kwargs)
        try:
            msg.html = render_template(template + '.html', **kwargs)
        except:
            pass
        thr = Thread(target=Mail.send_async_email, args=[app_vacens, msg])
        thr.start()
        print('email sent')
        return thr

    @staticmethod
    def send_emailmsg(to, subject, msgbody, **kwargs):
        app_vacens = current_app._get_current_object()
        msg = Message(subject, sender=app_vacens.config['MAIL_USERNAME'], recipients=to)
        msg.body = msgbody
        thr = Thread(target=Mail.send_async_email, args=[app_vacens, msg])
        thr.start()
        return thr

    @staticmethod
    def annul_demande(vac_ens):
        responsable = User.query.get(user.resp_id)
        mail_object = "[VacEns] Demande d'annulation de vacances ("+ user.nom + " " + user.prenom +")"
        template_base_name = "templates_vacEns/mails/"
        template = template_base_name + "annul_vacs"
        to = [MAIL_USERNAME]
        cc = []  #[user.email, doyen@esiee.fr]    
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   form=form
            )

    @staticmethod
    def vacs_demande(vac_ens):
        if vac_ens.status == 0:
            validator = User.query.get(vac_ens.user.resp_id)
        elif vac_ens.status == 1:
            validator = User.query.filter_by(role=77).first()
        if vac_ens.type_demande == 'Report':
            type_demande = 'de report'
        else:
            type_demande = 'd\'annulation'
        mail_object = "[VacEns] Demande " + type_demande + " de vacances ("+ vac_ens.user.nom + " " + vac_ens.user.prenom +")"
        template_base_name = "templates_vacEns/mails/"
        template = template_base_name + "demande_vacs"
        to = [MAIL_USERNAME]
        cc = [] #[user.email, doyen@esiee.fr]        
        Mail.send_email(to, mail_object, template, cc=cc,
                   validator=validator,
                   vac_ens=vac_ens
            )
    @staticmethod
    def resp_valid_demande(vac_ens):
        responsable = User.query.get(vac_ens.user.resp_id)
        if vac_ens.type_demande == 'Report':
            type_demande = 'de report'
        else:
            type_demande = 'd\'annulation'
        mail_object = "[VacEns] Retour sur votre demande " + type_demande + " de vacances"
        template_base_name = "templates_vacEns/mails/"
        template = template_base_name + "valid_vacs_resp"
        to = [MAIL_USERNAME]#[vac_ens.user.email]
        cc = [] # doyen ?
        Mail.send_email(to, mail_object, template, cc=cc,
                   responsable=responsable,
                   vac_ens = vac_ens
            )

    @staticmethod
    def dir_valid_demande(vac_ens):
        responsable = User.query.get(vac_ens.user.resp_id)
        if vac_ens.type_demande == 'Report':
            type_demande = 'de report'
        else:
            type_demande = 'd\'annulation'
        mail_object = "[VacEns] Retour sur votre demande " + type_demande + " de vacances"
        template_base_name = "templates_vacEns/mails/"
        template = template_base_name + "valid_vacs_dir"
        to = [MAIL_USERNAME]#[vac_ens.user.email]
        cc = [] # [doyen@esiee.fr, responsable.email]
        Mail.send_email(to, mail_object, template, cc=cc,
                   responsable=responsable,
                   vac_ens = vac_ens
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
        mail_object = "[VacEns] "
        template_base_name = "templates_vacEns/mails/"
        
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
