from flask_wtf import Form as FlaskForm
from wtforms import IntegerField
from wtforms import StringField, BooleanField, PasswordField, SubmitField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, NumberRange
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me', default=False)


class PriseForm(FlaskForm):
    fmt = '%d/%m/%Y'
    priseDateDebut = DateField('Date de début :', [InputRequired()],
                               format=fmt,  # format = '%m/%d/%Y',
                               description='Premier jour')
    # priseDateFin = DateField('priseDateFin', format='%d/%m/%Y')
    priseDateFin = DateField('Date de fin :', [InputRequired()], format=fmt)
    priseNbJours = IntegerField('Nombre de jours :',
                validators=[DataRequired(), NumberRange(min=1)])


class PriseFormChrome(FlaskForm):
    fmt = '%Y-%m-%d'
    priseDateDebut = DateField('Date de début :', [InputRequired()],
                               format=fmt,  # format = '%m/%d/%Y',
                               description='Premier jour')
    # priseDateFin = DateField('priseDateFin', format='%d/%m/%Y')
    priseDateFin = DateField('Date de fin :', [InputRequired()], format=fmt)
    priseNbJours = IntegerField('Nombre de jours :',
                validators=[DataRequired(), NumberRange(min=1)])


class annulationForm(FlaskForm):
    fmt = '%d/%m/%Y'
    annulationDateDebut = DateField('Date de début :', format=fmt)
    annulationDateFin = DateField('Date de fin :', format=fmt)
    annulationNbJours = IntegerField('Nombre de jours :',
                    validators=[DataRequired(), NumberRange(min=1)])
    annulationMotif = StringField('Motif', validators=[InputRequired()])


class annulationFormChrome(FlaskForm):
    fmt = '%Y-%m-%d'
    annulationDateDebut = DateField('Date de début :', format=fmt)
    annulationDateFin = DateField('Date de fin :', format=fmt)
    annulationNbJours = IntegerField('Nombre de jours :',
                    validators=[DataRequired(), NumberRange(min=1)])
    annulationMotif = StringField('Motif', validators=[InputRequired()])

class TestForm(FlaskForm):
    boo = BooleanField('Send email', default="checked")
    submit = SubmitField('Submit')


class AddUserForm(FlaskForm):
    # ,render_kw={"style":'width:50%'})
    nom = StringField('Nom :', [InputRequired()])
    prenom = StringField('Prénom :', [InputRequired()])
    dept = SelectField(u'Département', choices=[('ISYS', 'ISYS'), ('IT', 'IT'), ('MTEL', 'MTEL'), ('SEN', 'SEN')])
    login = StringField('login esiee (sans le @esiee.fr) :',
                        [InputRequired()])
    submit = SubmitField('Ajouter')

class AdminForm(FlaskForm):

    signature_direction = SubmitField('Extraction pour signature direction')
    historique_total = SubmitField('Historique des vacances de tous les utilisateurs')
    
    