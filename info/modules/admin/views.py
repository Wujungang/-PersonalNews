import datetime
import time
from flask import render_template, request, jsonify, g, session, current_app, abort, redirect, url_for

from info import db
from info.models import User, News,Category
from info.utils.common import user_login_data
from info.utils.image_storage import storage
from . import admin_blue


@admin_blue.route('/add_category',methods=['POST'])
def add_category():
    category_id = request.json.get('id')
    name = request.json.get('name')
    if category_id and name:
        category = Category.query.get(category_id)
        category.name = name
    elif not category_id:
        category = Category()
        category.name = name
        db.session.add(category)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500, errmsg='更新数据库失败')
    return jsonify(errno=200, errmsg='ok')


#admin分类编辑
@admin_blue.route('/news_category',methods=['GET','POST'])
def news_category():
    if request.method == 'GET':
        categories_list = []
        categories = Category.query.all()
        categories = categories
        for category in categories:
            categories_list.append(category.to_dict())
        categories_list.pop(0)
        return render_template('admin/news_type.html',categories_list = categories_list)








#admin新闻详情展示
@admin_blue.route('/news_edit_detail/<int:news_id>',methods=['GET','POST'])
def news_edit_detail(news_id):
    if request.method == 'GET':
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=500,errmsg='查询新闻失败')
        if not news:
            abort(404)
        categorirs = Category.query.all()
        categorirs.pop(0)
        categories_list = []
        for category in categorirs:
            categories_list.append(category.to_dict())
        data = {
            'news': news.to_dict(),
            'categories':categories_list
        }

        return render_template('admin/news_edit_detail.html',data=data)
    else:
        news_id = request.form.get("news_id")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")
        if not all([news_id,title,digest,content,category_id]):
            return jsonify(errno=500,errmsg='缺少参数')
        ret = None
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if index_image:
            ret = storage(index_image.read())
            news.index_image_url = 'http://prhl60xbx.bkt.clouddn.com/'+ret
        news.title = title
        news.digest = digest
        news.content = content
        news.category_id = category_id
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=500,errmsg='更新数据错误')
        return jsonify(errno=200,errmsg='ok')


#admin新闻编辑
@admin_blue.route('/news_edit')
def news_edit():
    p = request.args.get('p',1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='参数错误')
    try:
        paginate = News.query.filter(News.status==0).order_by(News.create_time.desc()).paginate(p,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erno=500,errmsg='数据库更新失败')
    news_list = []
    news = paginate.items
    pages = paginate.pages
    page = paginate.page
    for new in news:
        news_list.append(new.to_dict())

    data = {
        'news':news,
        'pages':pages,
        'page':page
    }
    return render_template('admin/news_edit.html',data=data)

@admin_blue.route('/news_review_detail/<int:news_id>',methods=['GET','POST'])
def news_review_detail(news_id):
    if request.method == 'GET':
        news = News.query.get(news_id)
        data = {
            'news':news.to_dict()
        }
        return render_template('admin/news_review_detail.html',data=data)
    else:
        news_id = request.json.get('news_id')
        action = request.json.get('action')
        if not all([news_id,action]):
            return jsonify(errno=500,errmsg='缺少参数')
        if action not in ['accept','reject']:
            return jsonify(errno=500,errmsg='参数错误')
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=500,errmsg='查询数据库失败')
        if action == 'accept':
            news.status = 0
        else:
            reason = request.json.get('reason')
            news.status = -1
            news.reason = reason
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=500,errmsg='数据库更新失败')
        return jsonify(errno=200,errmsg='ok')



#管理端新闻审核
@admin_blue.route('/news_review',methods=['GET','POST'])
def news_review():
    p = request.args.get('p',1)
    keyword = request.args.get('keyword')
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='参数错误')
    try:
        if not keyword:
            paginate = News.query.filter(News.status!=0).order_by(News.create_time.desc()).paginate(p,10,False)
        else:
            paginate = News.query.filter(News.status != 0,News.title.contains(keyword)).order_by(News.create_time.desc()).paginate(p, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500,errmsg='查询数据库失败')
    item_list = []
    for item in paginate.items:
        item_list.append(item.to_review_dict())
    context = {
        'news_list':item_list,
        'pages':paginate.pages,
        'page':paginate.page
    }
    return render_template('admin/news_review.html',context=context)


#管理端用户列表
@admin_blue.route('user_list')
def user_list():
    p = request.args.get('p',1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=505,errmsg='参数格式错误')
    try:
        paginate = User.query.filter(User.is_admin==False).order_by(User.last_login.desc()).paginate(p,100,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=500)
    user_list = paginate.items
    pages = paginate.pages
    page = paginate.page

    data = {
        'user_list':user_list,
        'pages':pages,
        'page':page
    }
    return render_template('admin/user_list.html',data=data)


#首页图表展示
@admin_blue.route('/user_count')
def user_count():
    #查询总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    #查询月新增人数
    mon_count = 0
    try:
        now = time.localtime()
        mon_begin = '%d-%02d-01'%(now.tm_year,now.tm_mon)
        mon_begin_date = datetime.datetime.strptime(mon_begin,'%Y-%m-%d')
        mon_count = User.query.filter(User.is_admin == False,User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    #查询日新增人数
    day_count = 0
    try:
        now = time.localtime()
        day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
        day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

#图标展示
    # 每日的用户登录活跃量
    # 存放X轴的时间节点
    active_date = []
    # 存放Y轴的登录量的节点
    active_count = []

    # 查询今天开始的时间 06月04日 00:00:00
    # 获取当天开始时时间字符串
    t = time.localtime()
    today_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    # 获取当前开始时时间对象
    today_begin_date = datetime.datetime.strptime(today_begin, '%Y-%m-%d')

    for i in range(0, 31):
        # 计算一天开始
        begin_date = today_begin_date - datetime.timedelta(days=i)
        # 计算一天结束
        end_date = today_begin_date - datetime.timedelta(days=(i - 1))

        # 将X轴对应的开始时间记录
        # strptime : 将时间字符串转成时间对象
        # strftime : 将时间对象转成时间字符串
        active_date.append(datetime.datetime.strftime(begin_date, '%Y-%m-%d'))

        # 查询当天的用户登录量
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
            active_count.append(count)
        except Exception as e:
            current_app.logger.error(e)

    # 反转列表：保证时间线从左到右递增
    active_date.reverse()
    active_count.reverse()

    data = {
        'total_count':total_count,
        'mon_count':mon_count,
        'day_count':day_count,
        'active_date':active_date,
        'active_count':active_count
    }
    return render_template('admin/user_count.html',data=data)




#admin主页
@admin_blue.route('/index')
@user_login_data
def admin_index():

    user = g.user
    if not user:
        return render_template('admin/login.html')
    if user.is_admin != True:
        return render_template('admin/login.html')

    data = {
        'user':user.to_dict()
    }
    return render_template('admin/index.html',data = data)


#管理员登录界面
@admin_blue.route('/login',methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin/login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user =  User.query.filter(User.mobile==username,User.is_admin == True).first()
        if not user:
            return redirect(url_for('index.index'))
        if not all([username,password]):
            return render_template('admin/login.html', errmsg='cuowu')
        user = User.query.filter(User.mobile==username).first()
        if not user:
            return render_template('admin/login.html', errmsg='cuowu')
        if not user.check_password(password):
            return render_template('admin/login.html', errmsg='cuowu')
        session['nick_name'] = user.nick_name
        session['user_id'] = user.id
        session['is_admin'] = True
        session['mobile'] = user.mobile
        data = {
            'user':user.to_dict()
        }
        return render_template('admin/index.html',data=data)