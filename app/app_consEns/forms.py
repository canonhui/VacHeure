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
    deIntitule = StringField('Intitulé* :', [InputRequired()])
    deNomEntreprise = StringField('Nom d\'entreprise* :', [InputRequired()])
    deAdrInfoExtra = StringField('Informations d\'adresse complémantaires :')
    deAdrRue = StringField('Rue + n°* :', [InputRequired()])
    deAdrCode = StringField('Code Postal* :', [InputRequired()])
    deAdrVille = StringField('Ville* :', [InputRequired()])
    deDateDebut = DateField('Date de début* :', [InputRequired()], format=fmt)
    deNbJours = IntegerField('Nombre de jours* :', 
                    validators=[DataRequired(), NumberRange(min=0)])


class DemandeFormChrome(FlaskForm):
    fmt = '%Y-%m-%d'
    deIntitule = StringField('Intitulé* :', [InputRequired()])
    deNomEntreprise = StringField('Nom d\'entreprise* :', [InputRequired()])
    deAdrInfoExtra = StringField('Informations d\'adresse complémantaires :')
    deAdrRue = StringField('Rue + n°* :', [InputRequired()])
    deAdrCode = StringField('Code Postal* :', [InputRequired()])
    deAdrVille = StringField('Ville* :', [InputRequired()])
    deDateDebut = DateField('Date de début* :', [InputRequired()], format=fmt)
    deNbJours = IntegerField('Nombre de jours* :', 
                    validators=[DataRequired(), NumberRange(min=0)])


class TestForm(FlaskForm):
    boo = BooleanField('Send email', default="checked")
    submit = SubmitField('Submit')


class AddUserForm(FlaskForm):
    # ,render_kw={"style":'width:50%'})
    nom = StringField('Nom :', [InputRequired()])
    prenom = StringField('Prénom :', [InputRequired()])
    email = EmailField('Email :', [InputRequired()])
    role = SelectField('Role :', choices=[('1', 'Ensegnant'), ('2', 'Responsable du département'), ('77', 'Admin')])
    dept = SelectField('Département :', choices=[('ISYS', 'ISYS'), ('IT', 'IT'), ('MTEL', 'MTEL'), ('SEN', 'SEN')])
    login = StringField('login esiee :',
                        [InputRequired()])
    submit = SubmitField('Ajouter')

class AdminForm(FlaskForm):

    signature_direction = SubmitField('Extraire toutes les demandes pour signature direction')
    historique_total = SubmitField('Historique des déclarations de tous les utilisateurs')

    