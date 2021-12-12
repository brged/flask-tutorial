import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db=get_db()
        # 在一个应用环境中，每次调用 get_db 都应当返回相同的连接
        assert db is get_db()
    
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    # 退出环境后， 连接应当已关闭
    assert 'close' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called=False
    
    def fake_init_db():
        Recorder.called=True
    # 使用 Pytest’s monkeypatch 固件来替换 init_db 函数
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    # runner 固件用于通过名称调用 init-db 命令
    result = runner.invoke(args=['init-db'])

    assert 'Initialized' in result.output
    assert Recorder.called