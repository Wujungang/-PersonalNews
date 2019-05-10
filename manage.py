from info import create_app,db
from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate



app = create_app('dev')


#将flask对象与迁移脚本关联
manager = Manager(app)
#迁移脚本中关联数据库与flask对象
Migrate(app,db)
#创建迁移数据库的对象及将迁移命令添加到数据库对象
manager.add_command('mysql',MigrateCommand)



if __name__ == '__main__':
    print(app.url_map)
    manager.run()