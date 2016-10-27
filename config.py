import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp-mail.outlook.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    QIUBAI_MAIL_SUBJECT_PREFIX = '[QIUBAI]'
    QIUBAI_MAIL_SENDER = 'QIUBAI Admin <shen.maoya@outlook.com>'
    QIUBAI_ADMIN = os.environ.get('QIUBAI_ADMIN')
    QIUBAI_POSTS_PER_PAGE = 20
    QIUBAI_FOLLOWERS_PER_PAGE = 50
    QIUBAI_COMMENTS_PER_PAGE = 30
    QIUBAI_SLOW_DB_QUERY_TIME = 0.5
    QIUBAI_UPLOAD_FOLDER = '/path/to/the/uploads'
    QIUBAI_ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
                                                                                                'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
                                                                                                 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                SECURE = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.QIUBAI_MAIL_SENDER,
            toaddrs=[cls.QIUBAI_ADMIN],
            subject=cls.QIUBAI_MAIL_SUBJECT_PREFIX + 'Application Error', credentials=credentials, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)

    sys.setdefaultencoding(default_encoding)
