from flask import session, g, current_app
from flask.json import jsonify
from functools import wraps
from info.models import User


def wjg(index):
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(4)
                return jsonify(errno=505,errmsg='用户信息不存在')
        g.user = user
        return view_func(*args,**kwargs)
    return wrapper