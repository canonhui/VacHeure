from flask_wtf import Form as FlaskForm
from wtforms import IntegerField
from wtforms import (StringField, BooleanField, PasswordField,
                     SubmitField, SelectField, RadioField)
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, InputRequired, NumberRange


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)


class DecForm(FlaskForm):
    fmt = '%d/%m/%Y'
    decDateDebut = DateField('Date de début :', [InputRequired()],
                               format=fmt,  # format = '%m/%d/%Y',
                               description='Premier jour')
    # decDateFin = DateField('decDateFin', format='%d/%m/%Y')
    decLieu = StringField('Lieu :', validators=[DataRequired()])
    decNbHeures = IntegerField('Nombre d\'heures :', 
                    validators=[DataRequired(), NumberRange(min=0)])
    #decEcoleCCI = BooleanField('Ecole de la CCI?', default=False)
    decEcoleCCI = RadioField('Ecole de la CCI?', choices=[('1', 'Oui'), ('0', 'Non')],
                    validators=[DataRequired()])


class DecFormChrome(FlaskForm):
    fmt = '%Y-%m-%d'
    decDateDebut = DateField('Date de début :', [InputRequired()],
                               format=fmt,  # format = '%m/%d/%Y',
                               description='Premier jour')
    # decDateFin = DateField('decDateFin', format='%d/%m/%Y')
    decLieu = StringField('Lieu :', validators=[DataRequired()])
    decNbHeures = IntegerField('Nombre d\'heures :', 
                    validators=[DataRequired(), NumberRange(min=0)])
    #decEcoleCCI = BooleanField('Ecole de la CCI?', default=False)
    decEcoleCCI = RadioField('Ecole de la CCI?', choices=[('1', 'Oui'), ('0', 'Non')],
                    validators=[DataRequired()])


class annulationForm(FlaskForm):
    fmt = '%d/%m/%Y'
    annulationDateDebut = DateField('annulationDateDebut', format=fmt)
    annulationDateFin = DateField('annulationDateFin', format=fmt)
    annulationNbJours = IntegerField('annulationNbJours', validators=[InputRequired()])
    annulationMotif = StringField('annulationMotif', validators=[InputRequired()])


class annulationFormChrome(FlaskForm):
    fmt = '%Y-%m-%d'
    annulationDateDebut = DateField('annulationDateDebut', format=fmt)
    annulationDateFin = DateField('annulationDateFin', format=fmt)
    annulationNbJours = IntegerField('annulationNbJours', validators=[InputRequired()])
    annulationMotif = StringField('annulationMotif', validators=[InputRequired()])

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
    extraction_cci = SubmitField('Extraire les demandes des écoles CCI')
    extraction_hors_cci = SubmitField('Extraire les demandes hors des écoles CCI')
    historique_total = SubmitField('Historique des déclarations de tous les utilisateurs')

    