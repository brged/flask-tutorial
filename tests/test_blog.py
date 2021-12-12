import pytest

from flaskr.db import get_db


def test_index(client, auth):
    response=client.get('/')
    # 当没有登录时，每个页面 显示登录或注册连接
    assert b'Login' in response.data
    assert b'Register' in response.data

    # 当登录之后，应当有一个注销连接
    auth.login()
    response=client.get('/')
    assert b'Logout' in response.data

    # index 索引视图应当显示已添加的测试帖子数据
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    # 作为作者登录之后，应当有 编辑博客的连接
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize(
    'path',
    ('/create',
    '/1/update',
    '/1/delete',)
)
def test_login_required(client, path):
    response=client.post(path)
    # 用户必须登录后才能访问 create 、 update 和 delete 视图
    assert response.headers['Location']=='http://localhost/auth/login'

def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db=get_db()
        db.execute('UPDATE post SET author_id=2 WHERE id =1')
        db.commit()
    
    # 登录test用户：user id: 1
    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code==403
    assert client.post('/1/delete').status_code==403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', ('/2/update', '/2/delete'))
def test_exists_required(client, auth, path):
    auth.login()
    # 如果要访问 post 的 id 不存在，那么 update 和 delete 应当返回 404 Not Found
    assert client.post(path).status_code==404


def test_create(client, auth, app):
    auth.login()
    # 对于 GET 请求， create 和 update 视图应当渲染和返回一个 200 OK 状态码
    assert client.get('/create').status_code==200
    # 当 POST 请求发送了合法数据后， create 应当在 数据库中插入新的帖子数据
    client.post('/create', data={'title': 'created', 'body': ''})
    with app.app_context():
        db=get_db()
        count=db.execute('SELECT count(id) FROM post').fetchone()[0]
        assert count == 2

def test_update(client, auth, app):
    auth.login()
    # 对于 GET 请求， create 和 update 视图应当渲染和返回一个 200 OK 状态码
    assert client.get('/1/update').status_code==200
    # 当 POST 请求发送了合法数据后， update 应当修改数据库中现存的数据
    client.post('/1/update', data={'title': 'updated', 'body': ''})
    with app.app_context():
        db=get_db()
        post=db.execute('SELECT * FROM post WHERE id =1').fetchone()
        print(post['title'])
        assert post['title']=='updated'


# 当数据 非法时，两者都应当显示一个出错信息
@pytest.mark.parametrize('path', ('/create', '/1/update'))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data



def test_delete(client, auth, app):
    auth.login()
    # delete 视图应当重定向到索引 URL 
    response=client.post('/1/delete')
    assert response.headers['Location']=='http://localhost/'

    with app.app_context():
        db=get_db()
        # 并且帖子应当从数据库中删除
        post=db.execute('SELECT * FROM post WHERE id=1').fetchone()
        assert post is None


