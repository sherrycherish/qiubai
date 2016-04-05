#coding: utf-8
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask.ext.login import login_required, current_user
from . import main
from .forms import PostForm, CommentForm
from .. import db
from ..models import User, Post, Comment
import sys
import datetime
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    offset8 = datetime.datetime.timedelta(hours=-8)
    offset24 = datetime.datetime.timedelta(hours=-24)
    if 8_hours:
        query = Post.query.filter(Post.timestamp2 >= offset8).all()
    if hot:
        query = Post.query.filter(Post.timestamp2 >= offset24).all()
    if cross:
        query = Post.query.all
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['SHERRY_BLOG_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)


@main.route('/post/<int:id>', methods =['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论发布成功')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['SHERRY_BLOG_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['SHERRY_BLOG_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)



@main.route('/')
@login_required
def eight_hours():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('8_hours', '', max_age=30*24*60*60)
    return resp


@main.route('/hot')
@login_required
def hot():
    resp = make_response(redirect(url_for('.hot')))
    resp.set_cookie('hot', '1', max_age=30*24*60*60)
    return resp


@main.route('/')
@login_required
def history():
    resp = make_response(redirect(url_for('.history')))
    resp.set_cookie('history', '2', max_age=30*24*60*60)
    return resp