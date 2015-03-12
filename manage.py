#!LS_env/bin/python

import os

from app import create_app, db
from app.models import Values5

from app.lionlib import *
from app.bmslion import BmsLion
import time


from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#app = Flask(__name__)

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app,db=db)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)
manager.add_command("runserver", Server(
    use_debugger = True,
    use_reloader = True)

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


    manager.run()

