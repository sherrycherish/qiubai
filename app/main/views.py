# -*- coding:utf-8 -*-
from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, Add, \
    CommentForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Like
from ..decorators import admin_required, permission_required
import sys
import datetime

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['QIUBAI_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    """
    关闭服务器的路由
    """
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    offset8 = datetime.datetime.now() + datetime.timedelta(hours=-8)
    offset24 = datetime.datetime.now() + datetime.timedelta(days=-1)
    query = db.session.query(Post).filter(Post.timestamp2 >= offset8)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config[
        'QIUBAI_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination)


@main.route('/hot', methods=['GET', 'POST'])
def hot():
    page = request.args.get('page', 1, type=int)
    offset8 = datetime.datetime.now() + datetime.timedelta(hours=-8)
    offset24 = datetime.datetime.now() + datetime.timedelta(days=-1)
    query = db.session.query(Post).filter(Post.timestamp2 >= offset24)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config[
        'QIUBAI_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('hot.html', posts=posts, pagination=pagination)


@main.route('/history', methods=['GET', 'POST'])
def history():
    page = request.args.get('page', 1, type=int)
    offset8 = datetime.datetime.now() + datetime.timedelta(hours=-8)
    offset24 = datetime.datetime.now() + datetime.timedelta(days=-1)
    query = db.session.query(Post).filter(Post.timestamp2 >= offset24)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config[
        'QIUBAI_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('history.html', posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    post.like_count = Like.query.get(Like.like_body == True).count()
    like = Like.query.get()
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


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['QIUBAI_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    form = Add()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    return render_template('add.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username


@main.route('/pic', methods=['GET', 'POST'])
def pic():
    page = request.args.get('page', 1, type=int)

    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page=current_app.config[
                                                                         'QIUBAI_POSTS_PER_PAGE'],
                                                                     error_out=False)
    posts = pagination.items
    return render_template('pic.html', posts=posts, pagination=pagination)


@main.route('/textnew', methods=['GET', 'POST'])
def textnew():
    page = request.args.get('page', 1, type=int)

    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page=current_app.config[
                                                                         'QIUBAI_POSTS_PER_PAGE'],
                                                                     error_out=False)
    posts = pagination.items
    return render_template('textnew.html', posts=posts, pagination=pagination)


@main.route('/text', methods=['GET', 'POST'])
def text():
    page = request.args.get('page', 1, type=int)

    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page=current_app.config[
                                                                         'QIUBAI_POSTS_PER_PAGE'],
                                                                     error_out=False)
    posts = pagination.items
    return render_template('text.html', posts=posts, pagination=pagination)


@main.route('/imgrank', methods=['GET', 'POST'])
def imgrank():
    page = request.args.get('page', 1, type=int)

    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page=current_app.config[
                                                                         'QIUBAI_POSTS_PER_PAGE'],
                                                                     error_out=False)
    posts = pagination.items
    return render_template('imgrank.html', posts=posts, pagination=pagination)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/upload', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def upload_file():
    if request.method == 'POST':
        file = request.file['file']
        if file and allowed_file(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
