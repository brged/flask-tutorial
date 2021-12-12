import os

from flask import Flask

def create_app(test_config=None):
    # create and config the app
    # instance_relative_config: 配置文件是相对于实例路径的
    app=Flask(__name__, instance_relative_config=True)
    # 设置默认的配置
    app.config.from_mapping(
        SECRET_KEY="dev", 
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )
    # 加载配置文件
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in 
        # 测试和开发的配置分离
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exists
    # 需要手动创建实例文件夹
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"
    
    # 注册 close_db 和 init_db_command 函数
    from . import db
    db.init_app(app)

    # 导入并注册 蓝图
    from . import auth
    app.register_blueprint(auth.bp)

    return app
