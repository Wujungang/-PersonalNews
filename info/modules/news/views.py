from flask import render_template, current_app, jsonify, g, abort
from flask import request,session

from info import db
from info.utils.common import user_login_data
from info.models import User, News, Comment,CommentLike
from . import news_blue



#关注与取消关注
@news_blue.route('/followed_user',methods=['GET','POST'])
@user_login_data
def followed_user():
    login_user = g.user
    if not login_user:
        return jsonify(errno=500,errmsg='用户未登录')

    user_id = request.json.get('user_id')
    action = request.json.get('action')
    if not all([user_id,action]):
        return jsonify(errno=500,errmsg='缺少参数')

    other = User.query.get(user_id)
    if not other:
        return jsonify(errno=500,errmsg='关注用户信息不存在')

    if action not in ['follow','unfollow']:
        return jsonify(errno=500, errmsg='关注用户信息不存在')


    if action == 'follow':
        if other not in login_user.followed:
            login_user.followed.append(other)
        else:
            abort(404)
    else:
        if other in login_user.followed:
            login_user.followed.remove(other)
        else:
            abort(404)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='用户关注失败')

    return jsonify(errno=200,errmsg='ok')



#评论点赞
@news_blue.route('/comment_like',methods=['post'])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        return jsonify(errno=4101,errmsg='用户不存在')
    comment_id = request.json.get('comment_id')
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([comment_id,news_id,action]):
        return jsonify(errno=505,errmsg='')
    commentlike_model = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == user.id).first()

    if action == 'add':
        if not commentlike_model:
            comment_like = CommentLike()
            comment_like.user_id = user.id
            comment_like.comment_id = comment_id
            try:
                db.session.add(comment_like)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                db.session.rollback()
                return jsonify(errno=505,errmsg='数据库更新失败')
    else:
        if commentlike_model:
            db.session.delete(commentlike_model)
            try:
                db.session.commit()
            except Exception as e:
                current_app.logger.error(3)
                db.session.rollback()
                return jsonify(errno=505,errmsg='数据库更新失败')
    return jsonify(errno=200,errmsg='ok')




#新闻评论
@news_blue.route('/news_comment',methods=['POST'])
@user_login_data
def news_comment():
    user = g.user
    if not user:
        return jsonify(errno=505,errmsg='用户未登录')
    news_id = request.json.get('news_id')
    comment_str = request.json.get('comment')
    parent_id = request.json.get('parent_id')
    if not all([news_id,comment_str]):
        return jsonify(errno=505,errmsg='缺少参数')
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=505,errmsg='新闻不存在')
    if not news:
        return jsonify(errno=505,errmsg='新闻不存在')
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=505,errmsg='数据库更新失败')

    return jsonify(errno=200,errmsg='ok',data=comment.to_dict())




#新闻收藏
@news_blue.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    user = g.user
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not user:
        return jsonify(errno=4101,errmsg='用户不存在')
    if not news_id:
        return jsonify(errno=505,errmsg='新闻不存在')
    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=505,errmsg='参数格式错误')
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=505,errmsg='数据库查询失败')
    if action == 'collect':
            user.collection_news.append(news)
    else:
            user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=504,errmsg='数据库提交失败')

    return jsonify(errno=200,errmsg='ok')

#新闻详情
@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    user = g.user
    click_news = News.query.order_by(News.clicks.desc()).limit(6)
    news = News.query.get(news_id)
    if not news:
        abort(404)
    is_collected = False
    if user:
        if news in g.user.collection_news:
            is_collected = True

    # 查询评论条数
    count = Comment.query.filter(Comment.news_id==news_id).all()
    count = len(count)

    #查询用户所有的点赞评论id
    if user:
        comment_list = CommentLike.query.filter(CommentLike.user_id==user.id).all()
        comment_id_list = [commentlike.comment_id for commentlike in comment_list]

    #查询评论列表
        comment_list = []
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
        for comment in comments:
            comment = comment.to_dict()
            is_like = False
            if comment['id'] in comment_id_list:
                is_like = True
            comment['is_like'] =  is_like
            like_count =len( CommentLike.query.filter(CommentLike.comment_id == comment['id']).all())
            comment['like_count'] = like_count
            comment_list.append(comment)
    else:
        comment_list = []
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
        for comment in comments:
            comment = comment.to_dict()
            is_like = False
            like_count = len(CommentLike.query.filter(CommentLike.comment_id == comment['id']).all())
            comment['like_count'] = like_count
            comment_list.append(comment)

    is_followed = False
    if user and news.user:
        if news.user in user.followed:
            is_followed = True

    data = {
        'user':user.to_dict() if user else None,
        'news':news.to_dict(),
        'click_news':click_news,
        'is_collected':is_collected,
        'comments':comment_list,
        'count':count,
        'is_followed':is_followed
    }
    return render_template('news/detail.html',data = data)