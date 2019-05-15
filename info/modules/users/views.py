from info.utils.image_storage import storage

from info.models import User
from . import user_blue
from info.utils.common import user_login_data
from flask import g, redirect, url_for, render_template, request, jsonify, current_app, session
from info import db


#个人头像
@user_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    user = g.user

    if request.method == 'GET':

        context = {
            'user':user
        }
        # return render_template('news/user_pic_info.html',context = context)
        return render_template('news/user_pic_info.html',context = context)
    if request.method == 'POST':
        image_file = request.files.get('avatar').read()
        if not image_file:
            return jsonify(errno=505,errmsg='图片上传失败')
        try:
            ret = storage(image_file)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=505,errmsg='图片保存失败')
        user.avatar_url = ret
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(3)
            return jsonify(errno=505,errmsg='图片上传失败')
        data = {
            'avatar_url': 'http://prhl60xbx.bkt.clouddn.com/' + ret
        }
        return jsonify(errno=200,errmsg='ok',data = data)





#个人基本信息
@user_blue.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method=='GET':
        context = {
            'user':user.to_dict()
        }
        return render_template('news/user_base_info.html',context=context)
    if request.method=='POST':
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')
        if not all([nick_name,signature,gender]):
            return jsonify(errno=505,errmsg='缺少参数')
        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=505,errmsg='数据库提交失败')
        session['nick_name'] = nick_name
        return jsonify(errno=200,errmsg='ok')



@user_blue.route('/info')
@user_login_data
def get_user_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user.to_dict()
    }
    return render_template('news/user.html',context=context)

