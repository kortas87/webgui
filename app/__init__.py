from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
#from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy

import config




bootstrap = Bootstrap()
mail = Mail()
#moment = Moment()
db = SQLAlchemy()

class MenuView:
    def __init__(self, view, name, module):
        self.view = view
        self.name = name
        self.module = module


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config.webgui_settings[config_name])
    config.webgui_settings[config_name].init_app(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    #moment.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    print("detecting modules...")
    
    for key in config.webgui_modules:

        # key is then used for class name
        configkey = key
        # we can have more instances of the same plugin with different settings (_suffix)
        more = key.split("_")
        if (len(more) == 2):
            key   = more[0]
            suffix = "_"+str(more[1])
        else:
            suffix = ""

        module = __import__('app.'+key)
        module = getattr(module, key)
        class_ = getattr(module, key)

        dev_object = class_(config.webgui_modules[configkey])
        #each module can do anything...
        dev_object.start()
        #save module instance
        config.modules[configkey] = {'obj':dev_object, 'enabled':True}
        # append menu list from each module
        for view,name in config.modules[configkey]['obj'].menu().items():
            config.menu_items[view+suffix] = MenuView(view+suffix, name, configkey)

    

    return app

