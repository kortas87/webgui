#!LS_env/bin/python

import os

import config

from app import create_app, db
from app.models import Values5
import signal
import sys

from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

def signal_handler(signal, frame):

    print ('You pressed Ctrl+C!')
    print ("Trying to terminate thread")
    for key in config.webgui_modules:
        #each module can do anything...
        config.modules[key]['obj'].terminate();
        print ("EXIT: "+str(key)+" OK")
    sys.exit(0)

def make_shell_context():
    return dict(app=app,db=db)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


class MenuView:
    def __init__(self, view, name, module):
        self.view = view
        self.name = name
        self.module = module

if __name__ == '__main__':
    
    # kill with ctrl+c
    signal.signal(signal.SIGINT, signal_handler)
    
    for key in config.webgui_modules:
        module = __import__('app.'+key)
        module = getattr(module, key)
        class_ = getattr(module, key)
        dev_object = class_(config.webgui_modules[key])
        #each module can do anything...
        dev_object.start()
        #save module instance
        config.modules[key] = {'obj':dev_object, 'enabled':True}
        # append menu list from each module
        for view,name in config.modules[key]['obj'].menu().items():
            config.menu_items[view] = MenuView(view, name, key) 

    #if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    manager.run()
