from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_login import current_user
from ..models import User

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Your old password:', validators=[DataRequired()])
    new_password1 = PasswordField('New password:', validators=[DataRequired(), EqualTo('new_password2', message='Passwords must match.')])
    new_password2 = PasswordField('Confirm your new password:', validators=[DataRequired()])
    submit = SubmitField('Change')

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('This password is incorect')

class ChangeEmailForm(FlaskForm):
    password = PasswordField('Enter your password:', validators=[DataRequired()])
    new_email1 = StringField('New email:', validators=[DataRequired(), EqualTo('new_email2', message='emails must match.'), Length(1, 64)])
    new_email2 = StringField('Confirm your new email:', validators=[DataRequired()])
    submit = SubmitField('Change')

    def validate_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Your password is incorrect')
    
    def validate_new_email1(self, field):
        email = User.query.filter_by(email=field.data)
        if list(email):
            raise ValidationError('This email is already in use')