import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = os.environ.get('DEBUG') or False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chefs.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

