from flaskr import create_app

# 唯一可以改变的行为是传递测试配置。如果没传递配置，那么会有一些缺省配置可 用，否则配置会被重载。
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

# 在本教程开头的部分添加了一个 hello 路由作为示例。它返回 “Hello, World!” ，因此测试响应数据是否匹配。
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b"Hello, World!"