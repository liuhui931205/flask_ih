# coding=utf-8
import redis

class Config(object):
    DEBUG = True

    SECRET_KEY = 'xPjqaXq3/DBlGnKBo1PC4JWdR3mj39jjG3m3QSHlmZQCWX7At19SlLCHtxJ+ofsf'

    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ih_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIST_DB = 3

    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT,db=REDIST_DB)
    PERMANENT_SESSION_LIFETIME = 86400

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ih_test'

config_dict = {
    'development':DevelopmentConfig,
    'production':ProductionConfig
}

