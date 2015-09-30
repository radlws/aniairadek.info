import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'rsvp_app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

from settings_local import *


