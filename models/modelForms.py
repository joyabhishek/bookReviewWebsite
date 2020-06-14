from flask_wtf import Form
from wtforms import StringField, PasswordField, validators
class RegistrationForm(Form):
	username = StringField('Username',[validators.Length(min=4, max=25)])
	password = PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('repeat Password')