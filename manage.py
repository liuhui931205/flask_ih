# coding=utf-8

# from flask_script import Manager
from flask_migrate import Manager,Migrate,MigrateCommand
from iHome import create_app,db
from iHome import models

app = create_app('development')

manage = Manager(app)
Migrate(app,db)
manage.add_command('db',MigrateCommand)


if __name__ == '__main__':
    # app.run()
    manage.run()
