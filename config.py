import redis
import logging


class Config(object):

    #配置秘钥
    SECRET_KEY = 'ZXC123'
    #开启调试模式
    DEBUG = True
    # 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@222.29.81.144:3306/information"
    #禁止动态追踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # flask_session的配置信息
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒
    #设置jsonify返回汉字不乱码
    JSON_AS_ASCII = False
class DevelopementConfig(Config):
    """开发模式下的配置"""
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """生产模式下的配置"""
    LOG_LEVEL = logging.ERROR

class UnitTsetConfig(Config):
    """生产模式下的配置"""
    pass

config = {
    'dev':DevelopementConfig,
    'pro':ProductionConfig,
    'test':UnitTsetConfig
}