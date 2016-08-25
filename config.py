import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ganz komplizierter Schluessel'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    #i = 0
    @staticmethod
    def init_app(app):
        #i = i+1
        print("start config...")
        pass

class DevelopmentConfig(Config):
    DEBUG=False

class TestingConfig(Config):
    DEBUG=False

class ProductionConfig(Config):
    DEBUG=False

webgui_settings = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
        }

# default variables
default_variables = {
  'uptime' : 0,                       # this contains uptime
  'first_view_mod'   : 'CustomAll',     # set default view by module's first view
  'first_view_name'  : 'view_customall',
  'refresh' : 5,                      # default refresh value [s]
}

# html menu
# will append item from each module automatically based on hook menu
menu_items        = {} # key, name
menu_items_module = {} # this hold key to module connection

#used for storing enabled modules 
modules = {}

#module configuration
webgui_modules = {}

webgui_modules['BmsLionSQL'] = {
    'db_filename':'todo.db',
    'db_scheme'  :'db_scheme.sql'
}

webgui_modules['FishLogger'] = {
    'name' : 'FishLogger',
}

#webgui_modules['BmsLion'] = {
#    '/dev/ttyACM0','/dev/ttyACM1',
#    '/dev/ttyUSB0',
#    '/dev/tty.usbmodem01',
#    #'/home/kortas/minicom.cap']
#}
webgui_modules['SendMail'] = {
    "SMTPserver":'smtp.seznam.cz', 
    'sender':'xxx@seznam.cz',
    'destination':'xxx@seznam.cz',
    "username":'xxx',
    'password':'x'
}
