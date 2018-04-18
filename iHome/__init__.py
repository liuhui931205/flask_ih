# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config_dict
from iHome.utils.commons import RegexConverter

db = SQLAlchemy()
redis_store = None



def create_app(config_name):

    app = Flask(__name__)
    con_cls = config_dict[config_name]
    app.config.from_object(con_cls)
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=con_cls.REDIS_HOST, port=con_cls.REDIS_PORT, db=con_cls.REDIST_DB)
    CSRFProtect(app)
    Session(app)
    app.url_map.converters['re'] = RegexConverter

    from iHome.api_1_0 import api
    app.register_blueprint(api,url_prefix='/api/v1.0')
    from iHome.web_html import html
    app.register_blueprint(html)



    return app