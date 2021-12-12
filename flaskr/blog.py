from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


## 索引
@bp.route('/')
def index():
    db=get_db()
    posts=db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id=u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method=='POST':
        title=request.form['title']
        body=request.form['body']
        error = None

        if not title:
            error='Title is required.'
        # elif not body:
        #     error='Body is required'
        
        if error is not None:
            flash(error)
        else:
            db=get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

"""update 和 delete 视图都需要通过 id 来获取一个 post ，并且 检查作者与登录用户是否一致。
为避免重复代码，可以写一个函数来获取 post ， 并在每个视图中调用它。"""
## check_author 参数的作用是函数可以用于在不检查作者的情况下获取一个 post 。
# 这主要用于显示一个独立的帖子页面的情况，因为这时用户是谁没有关系， 用户不会修改帖子
def get_post(id, check_author=True):
    post=get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id=u.id'
        ' WHERE p.id=?',
        (id,)
    ).fetchone()

    ## abort() 会引发一个特殊的异常，返回一个 HTTP 状态码。
    # 它有一个可选参数， 用于显示出错信息，若不使用该参数则返回缺省出错信息
    if post is None:
        # 404 表示“未找到”
        abort(404, "Post id {0} doesn't exist.".format(id))
    
    if check_author and post['author_id'] != g.user['id']:
        # 403 代表“禁止访问”
        abort(403)
    # 401 表示“未授权”，但是我们重定向到登录 页面来代替返回这个状态码
    #

    return post


# 如果没有指定 int: 而是仅仅写了 <id> ，那么将会传递一个字符串
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post=get_post(id)

    if request.method=='POST':
        title=request.form['title']
        body=request.form['body']
        error=None

        if not title:
            error='Title is required.'

        if error is not None:
            flash(error)
        else:
            db=get_db()
            db.execute(
                'UPDATE post SET title=?, body=?'
                ' WHERE id=?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post=get_post(id)
    db=get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))