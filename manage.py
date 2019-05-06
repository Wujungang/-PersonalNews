from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate
from config import Config

app = Flask(__name__)

# class Config(object):
#
#     #配置秘钥
#     SECRET_KEY = 'ZXC'
#     #开启调试模式
#     DEBUG = True
#     # 数据库的配置信息
#     SQLALCHEMY_DATABASE_URI = "mysql://root:123456@222.29.81.144:3306/information"
#     #禁止动态追踪
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     # redis配置
#     REDIS_HOST = "127.0.0.1"
#     REDIS_PORT = 6379
#     # flask_session的配置信息
#     SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
#     SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
#     SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
#     PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒

redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
#关联flask对象与Config对象
app.config.from_object(Config)
#关联flask对象与SQLAlchemy对象
db = SQLAlchemy(app)
#开启csrf保护
CSRFProtect(app)
#将Sessiom扩展与flask对象关联
Session(app)
#将flask对象与迁移脚本关联
manager = Manager(app)
#迁移脚本中关联数据库与flask对象
Migrate(app,db)
#创建迁移数据库的对象及将迁移命令添加到数据库对象
manager.add_command('db',MigrateCommand)

@app.route('/')
def index():
    redis_store.set('name','zxc')
    return 'index'

if __name__ == '__main__':
    manager.run()