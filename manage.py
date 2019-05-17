from info import create_app,db
from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate

from info.models import User

app = create_app('dev')


#将flask对象与迁移脚本关联
manager = Manager(app)
#迁移脚本中关联数据库与flask对象
Migrate(app,db)
#创建迁移数据库的对象及将迁移命令添加到数据库对象
manager.add_command('mysql',MigrateCommand)

# 脚本的使用 ： python manage.py createsuperuser -u admin -p 12345678 -m 18500000000
@manager.option('-u', '-username', dest='username')
@manager.option('-p', '-password', dest='password')
@manager.option('-m', '-mobile', dest='mobile')
def createsuperuser(username, password, mobile):
    """创建超级管理员用户的脚本函数"""

    if not all([username,password,mobile]):
        print('缺少必传参数')
    else:
        user = User()
        user.nick_name = username
        user.password = password
        user.mobile = mobile
        # 当is_admin为True时，才是管理员用户
        user.is_admin = True
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)


if __name__ == '__main__':
    print(app.url_map)
    manager.run()