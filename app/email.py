#-*- coding:utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)


def send_async_email(app, msg):
    """
    异步发送电子邮件
    """
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """
    发送电子邮件
    """
    app = current_app._get_current_object()
    msg = Message(app.config['SHERRY_BLOG_MAIL_SUBJECT_PREFIX'] + ' ' + \
                  subject, sender=app.config['SHERRY_BLOG_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


