from urllib.request import urlopen

from flask import g, request, redirect, session, current_app, abort

from app.models import WXUser
from app.utils.redis_util import redis_client
from app.utils.weixin_util import get_auth_url


def user_authentication():
    """
    用户身份认证
    :return:
    """
    g.wx_user = None
    # if request.endpoint.split('.')[-1] in ["get_open_upload_file_tokens", "index"]:
    #     return
    # current_app.logger.info('{}-{}'.format(request.headers, request.full_path))
    # wx_user = WXUser.select().where(WXUser.id.in_([23, 24])).get()
    # g.wx_user = wx_user
    # return
    token = request.headers.get('Authorization')
    if token:
        wx_user = WXUser.get_by_token(token)
        if wx_user:
            g.wx_user = wx_user  # g.admin
            return
    abort(401)
