from flask import render_template, current_app, jsonify
from flask import request,session

from info.models import User
from . import news_blue

# @news_blue.route('/detail/<int:news_id>',methods=['get'])
@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(errno=500,errmsg='用户登录信息不存在')

    user = User.query.get(user_id)
    data = {
        'user':user
    }
    return render_template('news/detail.html',data = data)