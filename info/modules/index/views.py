from . import index_blue
from info import redis_store
from info.models import User,News,Category
from flask import render_template, session, jsonify, g
from flask import current_app,request
from info.utils.common import user_login_data

@index_blue.route('/newslist')
def newslist():
    #获取数据
    #校验数据
    #最新分类的查询
    #除最新分类其他的新闻查询

    page = request.args.get('page',1)
    cid = request.args.get('cid',1)
    per_page = request.args.get('per_page',10)
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='数据格式错误')
    if cid == 1:
        news = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
    else:
        news = News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).paginate(page, per_page, False)
    items = news.items
    total_pages = news.pages
    cur_page = news.page
    news_dict_list = []
    for new in items:
        new = new.to_basic_dict()
        news_dict_list.append(new)
    data = {
        'news':news_dict_list,
        'total_pages':total_pages,
        'cur_page':cur_page
    }
    return jsonify(errno=200,errmsg='ok',data=data)

@index_blue.route('/logout')
def logout():
    session.pop('user_id')
    return jsonify(errno=200,errmsg='退出成功')


@index_blue.route('/')
@user_login_data
def index():

    #点击排行展示
    try:
        news = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='查询数据失败')
    news_click_list = []
    for new in news:
        new = new.to_basic_dict()
        news_click_list.append(new)


    user = g.user
    #查询商品分类
    categories_list = []
    categories = Category.query.all()
    for category in categories:
        category = category.to_dict()if category else None
        categories_list.append(category)

    data = {
        'user_info':user if user else None,
        'news':news_click_list,
        'categories':categories
    }

    return render_template('news/index.html',data=data)

@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """title左侧图标"""
    # return 'Users/zhangjie/Desktop/Information_29/info/static/news/favicon.ico'
    return current_app.send_static_file('news/favicon.ico')

