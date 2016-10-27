# -*- coding:utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordForgotForm, PasswordResetForm
import sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


@auth.route('/unconfirmed')
def unconfirmed():
    """未验证用户"""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    注册
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('一封认证邮件已经发到您的邮箱了,请打开邮箱点击链接确认注册.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """重置密码"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('您的密码修改成功.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """找回密码"""
    form = PasswordForgotForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, '重置你的密码',
                       'auth/email/change_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('请查看您的邮箱, 点击链接确认修改密码')
        return redirect(url_for('main.index'))
    return render_template('auth/forgot_password.html', form=form)
