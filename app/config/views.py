from . import config
from flask import render_template, url_for, redirect, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Note
from .. import db
from .forms import *
from ..email import send_email


@config.route('/menu')
@login_required
def menu():
    return render_template('config_menu.html')

@config.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password1.data
        db.session.commit()
        flash('You have changed your password')
        return redirect(url_for('main.index'))
    return render_template('change_password.html', form=form)

@config.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.new_email1.data
        current_user.confirmed = False
        db.session.commit()
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, 'Confirm Your Account',
                    'auth/email/confirm', user=current_user, token=token)
        flash('You changed your email')
        return redirect(url_for('main.index'))
    return render_template('change_email.html', form=form)

@config.route('/dark_mode')
@login_required
def dark_mode():
    if current_user.dark_mode:
        current_user.dark_mode = False
    else:
        current_user.dark_mode = True
    db.session.commit()
    return redirect(url_for('config.menu'))