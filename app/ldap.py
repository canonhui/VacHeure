import base64

import re

import csv

from ldap3 import Connection, ALL
from ldap3 import Server


from .forms import LoginForm


class Ldap:
    @staticmethod
    def connect():
        print('connect...')
        server = Server('ldap.esiee.fr', use_ssl=True, get_info=ALL)
        first_conn = Connection(server, user="uid=" + LoginForm().login.data + ",ou=Users,dc=esiee,dc=fr",
                                password=LoginForm().password.data)
        first_conn.open()
        first_conn.search('dc=esiee, dc=fr', "(&(objectclass=person)(uid=" + LoginForm().login.data + "))",
                          attributes=['sn', 'principalMail', 'googleMail',
                                      'telephoneNumber', 'displayName', 'roomNumber', 'givenName',
                                      'dateCreation', 'dateExpiration', 'annuairePresent', 'mailEDU', 'Name'])
        if len(first_conn.entries) > 0:
            from .models_commun import User
            name = base64.b64decode(str(first_conn.entries[0]['Prenom'])).decode('UTF-8')
            surname = base64.b64decode(str(first_conn.entries[0]['Nom'])).decode('UTF-8')
            email = str(first_conn.entries[0]['googleMail'])
            resp_id = User.query.filter_by(user_id=usr_resp[LoginForm().login.data]).first().get_id()
            role = 0
            user = [surname, name, email, resp_id, role]
            first_conn.bind()
            return user
        first_conn.bind()
        return None

    '''    @staticmethod
        def connect_simple():
            server = Server('ldap.esiee.fr', use_ssl=True, get_info=ALL)
            first_conn = Connection(server, user="uid=" + LoginForm().login.data + ",ou=Users,dc=esiee,dc=fr",
                                    password=LoginForm().password.data)
            first_conn.open()
            return first_conn.bind()
    '''

    @staticmethod
    def connect_simple():
        return True
