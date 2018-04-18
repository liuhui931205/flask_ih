# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ih_test'

app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route('/')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()
