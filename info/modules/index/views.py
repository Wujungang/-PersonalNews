from . import index_blue
from info import redis_store
from info.models import User
from flask import render_template, session, jsonify
from flask import current_app


@index_blue.route('/logout')
def logout():
    session.pop('user_id')
    return jsonify(errno=200,errmsg='退出成功')


@index_blue.route('/')
def index():
    user_id = session.get('user_id')
    user = User.query.filter(User.id==user_id).first()
    user = user.to_dict()if user else None
    data = {
        'user_info':user
    }


    return render_template('news/index.html',data=data)

@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """title左侧图标"""
    # return 'Users/zhangjie/Desktop/Information_29/info/static/news/favicon.ico'
    return current_app.send_static_file('news/favicon.ico')

