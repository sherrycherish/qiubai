#!/usr/bin/env python
#coding:utf-8
import os
from flask import Flask
from app import create_app, db
from app.models import User, Post, Comment, Like
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand8

app = create_app(os.getenv('QIUBAI_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Like=Like, Post=Post, Comment=Comment)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def deploy():
    """Run deployment tasks."""

    from flask.ext.migrate import upgrade
    from app.models import Role, User

    # 把数据库迁移到最新修订版本
    upgrade()

    # 创建用户角色
    Role.insert_roles()

    #让所有用户都关注此用户
    User.add_self_follows()


if __name__ == '__main__':
    app = Flask(__name__)
    manager.run()
