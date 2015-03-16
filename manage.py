#!LS_env/bin/python

import os

import config

from app import create_app, db
from app.models import Values5

from app.lionlib import *
from app.bmslion import BmsLion
import time


from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#app.config.from_object(config_wg.DevelopmentConfig)
#app = Flask(__name__)

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app,db=db)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    # run bms thread with serial com
    uptime = time.time()
    BmsLion.self = BmsLion()
   
    # assign data class
    BmsLion.self.datalayer = Datalayer()
   
    # creates new reading process
    BmsLion.self.start()

    # create SQL logging class
    #sql_i = SQLhandler()
    BmsLion.self.datalayer.sqllog = 0

    #when debbug mode is on and reload is not disabled this will prevent to run app twice
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        manager.run()

