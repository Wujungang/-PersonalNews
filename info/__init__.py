from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session
from flask import Flask, render_template
import os

from config import config
import logging
from logging.handlers import RotatingFileHandler
from flask_ckeditor import CKEditor

ckeditor = CKEditor()

#创建一个SQLAlchemy对象
db = SQLAlchemy()
redis_store = redis.StrictRedis(host='127.0.0.1', port=6379,decode_responses=True)#decode_response将数据转成str
def setup_log(config_name):
    """配置日志"""
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

def create_app(config_name):
    #配置项目日志
    setup_log(config_name)
    app = Flask(__name__)
    # 设置富文本编辑器的高度
    app.config['CKEDITOR_HEIGHT'] = 400
    app.config['CKEDITOR_SERVE_LOCAL'] = True
    #富文本编辑器向后端发送请求时的路由，默认没有蓝图，需要加上蓝图
    app.config['CKEDITOR_FILE_UPLOADER'] = 'user.upload'
    #获取当前文件的路径，方便下面拼接上传文件存放路径
    basedir = os.path.abspath(os.path.dirname(__file__))
    #拼接上传文件存放的路径
    app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
    #富文本编辑器
    ckeditor.init_app(app)

    # 关联flask对象与Config对象
    app.config.from_object(config[config_name])
    # 手动为SQLAlchemy对象执行init_app方法并传入app
    db.init_app(app)
    # global redis_store
    # redis_store = redis.StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT,decode_responses=True)
    # 开启csrf保护
    # CSRFProtect(app)
    # 将Sessiom扩展与flask对象关联
    Session(app)

    #注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    from info.modules.users import user_blue
    app.register_blueprint(user_blue)
    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)

    @app.errorhandler(404)
    def errorhandler(e):
        return render_template('news/404.html')

    @app.after_request
    def after_request(response):
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token",csrf_token)
        response.set_cookie("calis", 'calis')
        return response

    #注册自定义过滤器
    from info.utils.common import wjg
    app.add_template_filter(wjg,'wjg')

    return app


