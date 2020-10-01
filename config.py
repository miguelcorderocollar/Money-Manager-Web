import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "6549841231618"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "postgres://ddfbbyssvxvzgr:b41f77b5698320226a7cc8244498a954557f228bb88e78c8c04e6ed78b84b993@ec2-54-228-250-82.eu-west-1.compute.amazonaws.com:5432/dcbdnv7hgijo2v"
class DevelopmentConfig(Config):
    ENV="development"
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"