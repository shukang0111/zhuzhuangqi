from urllib.request import urlopen

from flask import g, request, redirect, session, current_app, abort

from app.models import WXUser
from app.utils.redis_util import redis_client
from app.utils.weixin_util import get_auth_url, get_auth2_access_token, get_wx_user_detail


def user_authentication():
    """
    用户身份认证
    :return:
    """
    # g.wx_user = None
    if request.endpoint.split('.')[-1] in ["get_open_upload_file_tokens"]:
        return
    # # current_app.logger.info('{}-{}'.format(request.headers, request.full_path))
    # # wx_user = WXUser.select().where(WXUser.id.in_([23, 24])).get()
    # # g.wx_user = wx_user
    # # return
    # token = request.headers.get('Authorization')
    # if token:
    #     wx_user = WXUser.get_by_token(token)
    #     if wx_user:
    #         g.wx_user = wx_user  # g.admin
    #         return
    # abort(401)
    openid = session.get("openid")
    current_app.logger.info(openid)
    code = request.args.get("code")
    redirect_url = request.url
    current_app.logger.info("{0}_{1}".format(code, redirect_url))
    if not openid:
        if not code:
            return redirect(get_auth_url(redirect_url))
        else:
            pass
            # item = get_auth2_access_token(code)
            # access_token = item.get("access_token")
            # openid = item.get("openid")
            # current_app.logger.info("openid")
            # user_info = get_wx_user_detail(access_token, openid)
            # nickname = user_info.get("nickname").encode('iso-8859-1').decode('utf-8')
            # headimgurl = user_info.get("headimgurl")
            # try:
            #     wx_user = WXUser.get_by_openid(openid)
            #     wx_user.nickname = nickname
            #     wx_user.avatar = headimgurl
            #     wx_user.save()
            #     current_app.logger.info("1_{}".format(wx_user.to_dict()))
            # except:
            #     wx_user = WXUser.new(openid, headimgurl, nickname)
            #     current_app.logger.info("2_{}".format(wx_user.to_dict()))
    return
