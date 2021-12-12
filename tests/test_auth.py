import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    # register 视图应当在 GET 请求时渲染成功
    assert client.get('/auth/register').status_code==200
    # 在 POST 请求中，表单数据合法时，该视图应当重定向到登录 URL 
    response = client.post('/auth/register', data={'username': 'a', 'password': 'a'})
    assert 'http://localhost/auth/login'==response.headers['Location']

    # 并且用户 的数据已在数据库中保存好
    with app.app_context():
        assert get_db().execute(
            "select * from user where username=?", ('a',)
        ).fetchone() is not None


# pytest.mark.parametrize 以不同的参数运行同一个测试
@pytest.mark.parametrize(
    ('username', 'password', 'message'), 
    (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
    )
)
# 数据非法时，应当显示出错信息
def test_register_validate_input(client, username, password, message):
    response=client.post('/auth/register', 
        data={'username': username, 'password': password},
    )
    # data 以字节方式包含响应的身体。如果想比较 Unicode 文本，请使用 get_data(as_text=True)
    assert message in response.data


# 登录之后 session 应当包含 user_id
def test_login(client, auth):
    assert client.get('/auth/login').status_code==200

    response=auth.login()
    assert response.headers['Location']=='http://localhost/'

    with client:
        client.get('/')
        assert session['user_id']==1
        assert g.user['username']=='test'

@pytest.mark.parametrize(
    ('username', 'password', 'message'),(
    ('test', 'a', b'Incorrect username or password.'),
    ('user_not_exist', 'test', b'Incorrect username or password.'),
))
def test_login_validate(auth, username, password, message):
    response=auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        # 注销之后， session 应当不包含 user_id 
        auth.logout()
        assert 'user_id' not in session