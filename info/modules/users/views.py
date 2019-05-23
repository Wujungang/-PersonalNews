import datetime
import os
import random

from info.utils.image_storage import storage
from info.models import User, Category, News
from . import user_blue
from info.utils.common import user_login_data
from flask import g, redirect, url_for, render_template, request, jsonify, current_app, session, abort, send_from_directory
from info import db
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success

@user_blue.route('/other_news_list')
@user_login_data
def other_news_list():
    user = g.user
    if not user:
        abort(404)
    p = request.args.get('p','1')
    p = int(p)
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    paginate = News.query.filter(News.user_id == user.id).paginate(p, 1, False)
    # 获取当前页数据
    news_list = paginate.items
    pages = paginate.pages
    page = paginate.page
    news_dict_list = []
    for i in news_list:
        news_dict_list.append(i.to_review_dict())
    data = {
        'news_list':news_dict_list,
        'total_page':pages,
        'current_page':page
    }
    return jsonify(errno=200, data=data)
    # 1.获取页数
    # page = request.args.get("p", '1')
    # other_id = request.args.get("user_id")
    #
    # # 2.校验参数
    # try:
    #     p = int(page)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=500, errmsg='参数错误')
    #
    # if not all([page, other_id]):
    #     return jsonify(errno=500, errmsg='缺少参数')
    #
    # # 3.查询用户数据
    # try:
    #     user = User.query.get(other_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=5000, errmsg='查询用户数据失败')
    # if not user:
    #     return jsonify(errno=500, errmsg='用户不存在')
    #
    # # 4.分页查询
    # try:
    #     paginate = News.query.filter(News.user_id == user.id).paginate(p, 4, False)
    #     # 获取当前页数据
    #     news_list = paginate.items
    #     # 获取当前页
    #     current_page = paginate.page
    #     # 获取总页数
    #     total_page = paginate.pages
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=500, errmsg='查询用户数据失败')
    #
    # # 5.构造响应数据
    # news_dict_list = []
    # for news_item in news_list:
    #     news_dict_list.append(news_item.to_review_dict())
    #
    # data = {
    #     "news_list": news_dict_list,
    #     "total_page": total_page,
    #     "current_page": current_page
    # }
    #
    # # 6.渲染界面
    # return jsonify(errno=200, errmsg='OK', data=data)




#其他用户的信息
@user_blue.route('/other_info')
@user_login_data
def other_info():
    user = g.user
    user_id = request.args.get('id')

    other = User.query.get(user_id)
    # paginate = News.query.filter(News.user_id == user.id).paginate(p, 1, False)
    if not other:
        abort(404)

    is_followed = False
    if user and other:
        if other in user.followed:
            is_followed = True
    context = {
        'user':user.to_dict() if user else None,
        'other':other.to_dict(),
        'is_followed':is_followed
    }
    return render_template('news/other.html',context=context)




#个人关注
@user_blue.route('/user_follow',methods=['GET','POST'])
@user_login_data
def user_follow():
    user = g.user
    p = request.args.get('p',1)
    p = int(p)
    paginates = user.followed.paginate(p,1,False)
    items = paginates.items
    pages = paginates.pages
    page = paginates.page

    user_list = []
    for i in items:
        user_list.append(i.to_dict())

    context = {
        'wjg123':user_list if user_list else [],
        'pages':pages,
        'page':page
    }
    return render_template('news/user_follow.html',context=context)






@user_blue.route('/news_list')
@user_login_data
def news_list():
    p = request.args.get('p',1)
    user = g.user
    p = int(p)
    news_list = News.query.filter(News.user_id == user.id).paginate(p,1,False)
    items = news_list.items
    pages = news_list.pages
    page = news_list.page
    data = {
        'news_list':items,
        'pages':pages,
        'page':page
    }
    return render_template('news/user_news_list.html',data=data)



@user_blue.route('/files/<filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


def gen_rnd_filename():
    filename_endfix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_endfix, str(random.randrange(1000, 10000)))

@user_blue.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[1].lower()
    # if extension not in ['jpg', 'gif', 'png', 'jpeg']:
    #     return upload_fail(message='Image only!')
    start_prefix = gen_rnd_filename()
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], start_prefix + f.filename  ))
    url = url_for('user.uploaded_files', filename= start_prefix + f.filename)
    print(url)
    return upload_success(url=url)


@user_blue.route('/news_release',methods=['GET','POST'])
@user_login_data
def news_release():
    user = g.user
    if request.method == 'GET':
        category_list = []
        categories = Category.query.all()
        for category in categories:
            category_list.append(category.to_dict())
        category_list.pop(0)
        return render_template('news/user_news_release.html',category_list = category_list)

    if request.method == 'POST':
        title = request.json.get('title')
        category_id = request.json.get('category_id')
        digest = request.json.get('digest')
        source = "个人发布"
        # index_image = request.json.get('index_image').read()
        content = request.json.get('ckeditor')
        # if not all([title,category_id,digest,index_image,content]):
        #     return jsonify(errno=505,errmsg='缺少参数')
        #保存图片
        # try:
        #     ret = storage(index_image)
        # except Exception as e:
        #     current_app.logger.error(e)
        #     return jsonify(errno=505,errmsg='新闻发布失败')

        news = News()
        news.title = title
        news.category_id = category_id
        news.digest = digest
        # news.index_image_url = 'http://prhl60xbx.bkt.clouddn.com/' + ret
        news.content = content
        news.user_id = user.id
        news.status = 1
        news.source = source

        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=505,errmsg='新闻发送失败')
        return jsonify(errno=200,errmsg='ok')

#用户收藏信息
@user_blue.route('/user_collection',methods=['GET'])
@user_login_data
def user_collection():
    user = g.user
    if not user:
        return jsonify(errno=505,errmsg='用户未登录')
    p = request.args.get('p',1)
    if not int(p):
        return jsonify(errno=505,errmsg='参数格式错误')
    p = int(p)
    try:
        paginates = user.collection_news.paginate(p,3,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=505,errmsg='查询数据库失败')
    news_list = paginates.items
    pages = paginates.pages
    page = paginates.page

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    data = {
        'news_dict_list':news_dict_list,
        'pages':pages,
        'page':page
    }
    return render_template('news/user_collection.html',data=data)


#修改密码
@user_blue.route('/pass_info',methods=['GET','POST'])
@user_login_data
def pass_info():
    user = g.user
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        if not all([old_password,new_password]):
            return jsonify(errno=505,errmsg='缺少参数')
        if not user.check_password(old_password):
            return jsonify(errno=505,errmsg='密码错误')
        user.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=505,errmsg='更新数据失败')
        return jsonify(errno=200,errmsg='ok')




#个人头像
@user_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    user = g.user

    if request.method == 'GET':

        context = {
            'user':user.to_dict()
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

