#!/Users/chuchu/.virtualenvs/cp-bucketlist/bin/python3

""" Keeps track of all the commands and handles how they are called from the command line. """

import os
import unittest

from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app

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

@manager.command
def test():
    """ Runs the unit tests for the bucketlist api """
    tests = unittest.TestLoader().discover('./tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
