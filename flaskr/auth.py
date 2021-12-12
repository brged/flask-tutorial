import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint("auth", __name__, "/auth")

"""当用访问 /auth/register URL 时， register 视图会返回用于填写注册 内容的表单的 HTML 。
当用户提交表单时，视图会验证表单内容，然后要么再次 显示表单并显示一个出错信息，
要么创建新用户并显示登录页面。"""

## 注册
@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
        db=get_db()
        error=None
        # 判断非空
        if not username:
            error="Username is required."
        elif not password:
            error="Password is required."
        elif db.execute("SELECT id FROM user WHERE username = ?", username).fetchone() is not None:
            # 判断用户名是否存在
            error = "User {} is already registered.".format(username)
        # 通过校验
        if error is None:
            db.execute("INSERT INTO user (username, password) VALUES (?, ?)", username, generate_password_hash(password))
            db.commit()
            return redirect(url_for("auth.login"))
        # 用于储存在渲染模块时可以调用的信息
        flash(error)
    
    # 非post请求返回注册页
    return render_template("auth/register.html")


## 登录
@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db=get_db()
        error=None

        if not username:
            error="Username is required."
        elif not password:
            error="Password is required."
        
        user = db.execute("SELECT * FROM user WHERE username =?", username).fetchone()
        # if user is None:
        #     error="Incorrect username."
        # elif not check_password_hash(user["password"], password):
        #     error="Incorrect password."
        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect username or password."
        
        if error is None:
            session.clear()
            session["user_id"]=user["id"]
            return redirect(url_for("index"))
    
    return render_template("auth/login.html")

# 在视图函数之前运行的函数，不论其 URL 是什么
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    # 判断用户请求时session中是否有user_id，即是否登录成功
    if user_id is None:
        g.user=None
    else:
        g.user=get_db().execute("SELECT * FROM user WHERE id = ?", user_id).fetchone()

## 注销
@bp.route("/logout")
def logout():
    session.clear()
    redirect(url_for("index"))

# 用户登录以后才能创建、编辑和删除博客帖子。在每个视图中可以使用 装饰器 来完成这个工作。
"""装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。
新的函数检查用户 是否已载入。如果已载入，那么就继续正常执行原视图，否则就重定向到登录页面。 
我们会在博客视图中使用这个装饰器。"""
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view