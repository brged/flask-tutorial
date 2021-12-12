import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if "db" not in g:
        # g 是一个特殊对象，独立于每一个请求
        g.db=sqlite3.connect(
            # current_app 是另一个特殊对象，该对象指向处理请求的 Flask 应用
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # 告诉连接返回类似于字典的行，这样可以通过列名称来操作数据
        g.db.row_factory=sqlite3.Row
    
    return g.db

def close_db(e=None):
    """close_db 通过检查 g.db 来确定连接是否已经建立。如果连接已建立，那么就关闭连接。\\
        以后会在应用工厂中告诉应用 close_db 函数，这样每次请求后就会 调用它。"""
    db = g.pop("db", None)

    if db is not None:
        db.close()

# 运行schema.sql文件中的SQL命令
def init_db():
    db= get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """close_db 和 init_db_command 函数在应用实例中注册"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)