from flask import abort, g, request

from .models import db


def before_app_request() -> None:
    """请求前全局钩子函数"""
    if not request.blueprint:
        abort(404)
    g.ip = request.headers.get('X-Forwarded-For') or request.headers.get('X-Real-Ip')  # g.ip
    db.connect(reuse_if_open=True)


def teardown_app_request(e: Exception=None) -> None:
    """请求后全局钩子函数"""
    db.close()
