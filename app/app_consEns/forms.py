from flask_wtf import Form as FlaskForm
from wtforms import IntegerField
from wtforms import (StringField, BooleanField, PasswordField,
                     SubmitField, SelectField, RadioField)
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, InputRequired, NumberRange
from flask import request

class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)


class DemandeForm(FlaskForm):
    fmt = '%d/%m/%Y'
    deSujet = StringField('Sujet* :', [InputRequired()])
    deNomEntreprise = StringField('Nom d\'entreprise* :', [InputRequired()])
    deAdrInfoExtra = StringField('Informations d\'adresse complémantaires :')
    deAdrRue = StringField('Rue + n°* :', [InputRequired()])
    deAdrCode = StringField('Code Postal* :', [InputRequired()])
    deAdrVille = StringField('Ville* :', [InputRequired()])
    deDateDebut = DateField('Date de début* :', [InputRequired()], format=fmt)
    deNbJours = IntegerField('Nombre de jours* :', 
                    validators=[DataRequired(), NumberRange(min=1)])


class DemandeFormChrome(FlaskForm):
    fmt = '%Y-%m-%d'
    deSujet = StringField('Sujet* :', [InputRequired()])
    deNomEntreprise = StringField('Nom d\'entreprise* :', [InputRequired()])
    deAdrInfoExtra = StringField('Informations d\'adresse complémantaires :')
    deAdrRue = StringField('Rue + n°* :', [InputRequired()])
    deAdrCode = StringField('Code Postal* :', [InputRequired()])
    deAdrVille = StringField('Ville* :', [InputRequired()])
    deDateDebut = DateField('Date de début* :', [InputRequired()], format=fmt)
    deNbJours = IntegerField('Nombre de jours* :', 
                    validators=[DataRequired(), NumberRange(min=1)])

class AdminForm(FlaskForm):
    signature_direction = SubmitField('Extraire toutes les demandes pour signature direction')
    historique_total = SubmitField('Historique des déclarations de tous les utilisateurs')

    