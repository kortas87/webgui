#!LS_env/bin/python

import os

import config

from app import create_app, db
from app.models import Values5

import time


from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app,db=db)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    # run bms thread with serial com
    uptime = time.time()
    
    for key in config.webgui_modules:
        module = __import__('app.'+key)
        module = getattr(module, key)
        class_ = getattr(module, key)
        dev_object = class_(config.webgui_modules[key])
        #each module can do anything...
        dev_object.start()
        #save module instance
        config.modules[key] = {'obj':dev_object, 'enabled':True} 
        #dev_object.self = dev_object

    #if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    manager.run()
