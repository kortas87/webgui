#!LS_env/bin/python

import os
import config

from app import create_app, db
from app.models import Values5

import signal
import sys

from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('default')

