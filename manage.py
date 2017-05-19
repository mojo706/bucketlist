""" Keeps track of all the commands and handles how they are called from the command line. """

import os

from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from app import models

app = create_app(config_name=os.getenv('FLASK_CONFIG'))
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db',MigrateCommand)

@manager.command
def initdb():
    """ initialise the database with creation of tables """
    db.create_all()
    db.session.commit()

@manager.command
def dropdb():
    """ Deletes database """
    if prompt_bool("Are you sure you want to destroy all your data"):
        db.drop_all()

if __name__ == '__main__':
    manager.run()
