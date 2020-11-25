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
    if request.endpoint.split('.')[-1] in ["get_open_upload_file_tokens", "index"]:
        return
    # openid = session.get("openid")
    # current_app.logger.info(openid)
    # code = request.args.get("code")
    # redirect_url = request.url
    # current_app.logger.info("{0}_{1}".format(code, redirect_url))
    # if not openid:
    #     if not code:
    #         return redirect(get_auth_url(redirect_url), code=200)
    #     else:
    #         pass
    # return
    token = request.headers.get('Authorization')
    if token:
        wx_user = WXUser.get_by_token(token)
        if wx_user:
            g.wx_user = wx_user  # g.admin
            return
    abort(401)
