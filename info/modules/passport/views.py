import random
import re
from . import passport_blue
from info.models import User
from info import redis_store,db
from info.utils.captcha.captcha import captcha
from flask import request, current_app, jsonify,session,make_response,abort
from datetime import datetime




@passport_blue.route('/login',methods=['POST'])
def login():
    data_dict = request.json
    mobile = data_dict.get('mobile')
    password = data_dict.get('password')
    #校验参数
    if not all([mobile,password]):
        return jsonify(errno=400,errmsg='缺少验证码')
    #根据手机号查询用户信息
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='用户名或密码错误')
    if not user:
        return jsonify(errno=500,errmsg='用户名或密码错误')
    #校验密码
    if not user.check_password(password):
        return jsonify(errno=500,errmsg='用户名或密码错误')
    session['user_id'] = user.id
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='设置日期失败')
    return jsonify(errno=200,errmsg='ok')







@passport_blue.route('/register',methods=['POST'])
def register():
    data_dict = request.json
    mobile = data_dict.get('mobile')
    smscode = data_dict.get('smscode')
    password = data_dict.get('password')
    if not all([mobile,smscode,password]):
        current_app.logger.error('缺少信息')
        return jsonify(errno='400',errmsg='缺少信息')
    #查询短信验证码
    try:
        smscode_server = redis_store.get('SMS:'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=400,errmsg='查询手机号失败')
    if not smscode_server == smscode:
        current_app.logger.error('输入的短信验证码失败')
        return jsonify(errno=400,errmsg='输入的短信验证码失败')
    user = User()
    try:
        user.mobile = mobile
        user.nick_name = mobile
        user.password = password
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=400,errmsg='创建数据失败')
    session['user_id'] = user.id
    return jsonify(errno=200,errmsg='ok')







@passport_blue.route('/sms_code',methods=['post'])
def sms_code():
    data_dict = request.json
    mobile = data_dict.get('mobile')
    image_code = data_dict.get('imageCode')
    image_code_id = data_dict.get('imageCodeId')
    if not all([mobile,image_code,image_code_id]):
        current_app.logger.error('信息不全')
        return jsonify(errno=404,errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        current_app.logger.error('手机号格式不正确')
        return jsonify(errno=404,errmsg='手机号格式错误')
    try:
        image_code_id_server = redis_store.get('uuid:'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=404,errmsg='图片验证码错误')
    if not image_code_id_server.lower() == image_code.lower():
        current_app.logger.error('图片验证码错误')
        return jsonify(errno=404,errmsg='图片验证码错误')
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.error('短信验证码为;%s'%sms_code)
    redis_store.set('SMS:'+mobile,sms_code,60*60)
    return jsonify(errno=200,errmsg='ok')


@passport_blue.route('/image_code',methods=['GET'])
def image_code():
    code_id = request.args.get('code_id')
    if not code_id:
        abort(403)
        current_app.logger.error('找不到uuid')
    name,text,image = captcha.generate_captcha()
    current_app.logger.error(text)
    try:
        redis_store.set('uuid:'+code_id,text,60*60)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response



