from . import auth
from ..email import send_email
from flask import render_template, url_for, redirect, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from .forms import *
from ..models import User
from .. import db

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.keep_logged.data)
            next = url_for('main.index')
            return redirect(next)
        flash('Invalid email or password. ')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                    'auth/email/confirm', user=user, token=token)
        flash('You must confirm your email.')
        login_user(user, True)
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You confirmed your email')
        return redirect(url_for('main.index'))
    else:
        flash('Invalid token, or this token has expired')
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')

@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
    if not current_user.confirmed:
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, 'Confirm Your Account',
                    'auth/email/confirm', user=current_user, token=token)
        flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data)[0]
        token = user.generate_confirmation_token()
        send_email(user.email, 'Forgot your password?',
                    'mail/lose_password', user=user, token=token)
        flash('We sent an email for you.')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html', form=form)

@auth.route('/remember_password/<token>', methods=['GET', 'POST'])
def remember_password(token):
    id_ = User.return_id(token=token)
    users_id = [user.id for user in User.query.all()]
    if id_ not in users_id:
        flash('This token is invalid or has expired')
        return redirect(url_for('auth.login'))
    user = User.query.get(id_)

    form = NewPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('You have changed your password')
        return redirect(url_for('auth.login'))
    return render_template('remember_password.html', form=form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.confirmed \
               and request.endpoint \
               and request.blueprint != 'auth' \
               and request.blueprint != 'config'\
               and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))