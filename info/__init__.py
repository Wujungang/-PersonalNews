from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask import Flask
from config import config

#创建一个SQLAlchemy对象
db = SQLAlchemy()

redis_store = redis.StrictRedis(host='127.0.0.1', port=6379,decode_responses=True)

def create_app(config_name):
    app = Flask(__name__)
    # 关联flask对象与Config对象
    app.config.from_object(config[config_name])
    # 手动为SQLAlchemy对象执行init_app方法并传入app
    db.init_app(app)
    # global redis_store
    # redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT,decode_responses=True)
    # 开启csrf保护
    CSRFProtect(app)
    # 将Sessiom扩展与flask对象关联
    Session(app)
    return app
