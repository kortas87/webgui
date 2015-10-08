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

# default variables
default_variables = {
  'uptime' : 0,                          # this contains uptime
  'first_view_mod'   : 'BmsLionModbus',  # set default view by module's first view
  'first_view_name'  : 'view_modulesm',
  'refresh' : 1,                         # default refresh value [s]
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

#webgui_modules['BmsLion'] = {
#    '/dev/ttyACM0','/dev/ttyACM6',
#    '/dev/ttyUSB1',
#    '/dev/tty.usbmodem01',
#    #'/home/kortas/minicom.cap']
#}

webgui_modules['BmsLionModbus'] = {
    'modbus_timeout' : 0.1,    # longest response must fit inside this time
    'modbus_speed'   : 9600,
    'sleeptime_comm' : 0.5,     # sleeptime between modbus requests
    'debug_mode'     : True,
    'num_cell_modules': 18,
    'ports' : { '/dev/ttyUSB0',
                '/dev/ttyUSB1',
                '/dev/ttyUSB2',
                '/dev/tty.usbmodem01'
              }
}

webgui_modules['SendMail'] = {
    "SMTPserver":'smtp.seznam.cz', 
    'sender':'xxx@seznam.cz',
    'destination':'xxx@seznam.cz',
    "username":'xxx',
    'password':'x'
}
