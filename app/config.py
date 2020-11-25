from logging import Formatter
from os import getenv

from flask import Flask, session
from flask.logging import default_handler

from .hooks import before_app_request, teardown_app_request
from .misc import CustomJSONEncoder
from .blueprints.admin_api import bp_admin_api
from .blueprints.admin_ext import bp_admin_ext
from .blueprints.user_api import bp_user_api
# from .valid_token import update_yz_token


class Config:
    """配置"""

    SECRET_KEY = 'zhuzhuangqi'

    SERVER_NAME = getenv('SERVER_NAME')

    # blueprint
    BP_SUB_DOMAIN = {
        'admin': getenv('SUB_DOMAIN_ADMIN'),
        'user': getenv('SUB_DOMAIN_USER')
    }
    BP_URL_PREFIX = {
        'admin_api': '/api' if SERVER_NAME else '/api.admin',
        'admin_ext': '/ext' if SERVER_NAME else '/ext.admin',
        'user_api': '/api' if SERVER_NAME else '/api.user'
    }

    @classmethod
    def init_app(cls, app: Flask) -> None:
        """初始化flask应用对象"""
        app.logger.setLevel('INFO')
        default_handler.setLevel('INFO')
        default_handler.setFormatter(Formatter('[%(asctime)s] %(pathname)s:%(lineno)d [%(levelname)s] %(message)s'))
        app.before_request(before_app_request)
        app.teardown_request(teardown_app_request)
        app.json_encoder = CustomJSONEncoder
        sub, url = cls.BP_SUB_DOMAIN, cls.BP_URL_PREFIX
        app.register_blueprint(bp_admin_api, subdomain=sub.get('admin'), url_prefix=url.get('admin_api'))
        app.register_blueprint(bp_admin_ext, subdomain=sub.get('admin'), url_prefix=url.get('admin_ext'))
        app.register_blueprint(bp_user_api, subdomain=sub.get('user'), url_prefix=url.get('user_api'))
