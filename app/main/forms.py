#coding: utf-8
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length
from flask.ext.pagedown.fields import PageDownField
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)

class PostForm(Form):
    body = PageDownField("分享一件新鲜事...")
    submit = SubmitField('发表')


class CommentForm(Form):
    body = StringField('写下你的评论:')
    submit = SubmitField('发表')


