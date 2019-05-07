from flask import Flask
from info import create_app,db
from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate
from info import redis_store
import redis

app = create_app('dev')

# SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
# SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
# SESSION_REDIS = redis.StrictRedis(host='127.0.0.1', port=6379)  # 使用 redis 的实例
# PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒
# redis_store = redis.StrictRedis(host='127.0.0.1', port=6379,decode_responses=True)

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