from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from app.app_vacens import mail, models
from enum import Enum


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
    def annul_demande(user,form):
        responsable = models.User.query.get(user.resp_id)
        mail_object = "[VacEns] Demande d'annulation de vacances ("+ user.nom + " " + user.prenom +")"
        template_base_name = "mails/"
        template = template_base_name + "annul_vacs"
        to = ['jf.bercher@esiee.fr'] #[responsable.email]
        cc = ['abdul.alhazreb@gmail.com']  #[user.email, doyen@esiee.fr]    
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   form=form
            )

    @staticmethod
    def report_demande(user,form):
        responsable = models.User.query.get(user.resp_id)
        mail_object = "[VacEns] Demande de report de vacances ("+ user.nom + " " + user.prenom +")"
        template_base_name = "mails/"
        template = template_base_name + "report_vacs"
        to = ['jf.bercher@esiee.fr'] #[responsable.email]
        cc = ['abdul.alhazreb@gmail.com'] #[user.email, doyen@esiee.fr]        
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   form=form
            )
    @staticmethod
    def resp_valid_demande(user, vacs):
        responsable = models.User.query.get(user.resp_id)
        mail_object = "[VacEns] Retour sur ta demande d'annulation ou de report de vacances"
        template_base_name = "mails/"
        template = template_base_name + "valid_vacs_resp"
        to = ['jf.bercher@esiee.fr'] #[user.email]
        cc = [] # doyen ?
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   vacs = vacs
            )

    @staticmethod
    def dir_valid_demande(user, vacs):
        responsable = models.User.query.get(user.resp_id)
        mail_object = "[VacEns] Retour sur ta demande d'annulation ou de report de vacances"
        template_base_name = "mails/"
        template = template_base_name + "valid_vacs_dir"
        to = ['jf.bercher@esiee.fr'] #[user.email]
        cc = [] # [doyen@esiee.fr, responsable.email]
        Mail.send_email(to, mail_object, template, cc=cc,
                   user=user,
                   responsable=responsable,
                   vacs = vacs
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
        responsable = models.User.query.get(user.resp_id)
        mail_object = "[VacEns] "
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
