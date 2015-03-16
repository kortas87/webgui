import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ganz komplizierter Schluessel'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    @staticmethod
    def init_app(app):
        print("start...")
        pass

class DevelopmentConfig(Config):
    DEBUG=True

class TestingConfig(Config):
    DEBUG=True

class ProductionConfig(Config):
    DEBUG=True

webgui_settings = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
        }


