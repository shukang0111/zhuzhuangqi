from flask import request, g, current_app, session, render_template

from . import bp_user_api
from ...api_utils import *
from ...libs.kodo.kodo_api import KodoApi
from ...models import WXUser
from ...utils.weixin_util import get_auth2_access_token, get_wx_user_detail


@bp_user_api.route('/', methods=['GET'])
def index():
    """小程序回调"""
    code = request.args.get("code")
    current_app.logger.info(code)

    item = get_auth2_access_token(code)
    access_token = item.get("access_token")
    openid = item.get("openid")
    current_app.logger.info("openid")
    user_info = get_wx_user_detail(access_token, openid)
    nickname = user_info.get("nickname")
    headimgurl = user_info.get("headimgurl")
    try:
        wx_user = WXUser.get_by_openid(openid)
        wx_user.nickname = nickname
        wx_user.avatar = headimgurl
        wx_user.save()
        current_app.logger.info("1_{}".format(wx_user.to_dict()))
    except:
        wx_user = WXUser.new(openid, headimgurl, nickname)
        current_app.logger.info("2_{}".format(wx_user.to_dict()))
    # session['openid'] = openid
    # current_app.logger.info(openid)

    data = {
        "token": wx_user.gen_token()
    }
    return api_success_response(data)
    # return render_template("index.html")


@bp_user_api.route('/wx_user/', methods=['GET'])
def get_wx_user_center_info():
    """查询微信用户个人信息"""
    # openid = session.get("openid")

    # wx_user = WXUser.get_by_openid(openid)
    # wx_user = WXUser.select().where(WXUser.openid == openid).get()
    # current_app.logger.info(wx_user.id)
    wx_user = g.wx_user
    data = {
        "wx_user": wx_user.to_dict()
    }
    return api_success_response(data)


@bp_user_api.route('/wx_user/center/edit/', methods=['POST'])
def edit_wx_user_info():
    """个人中心信息更新"""
    wx_user_id, avatar, nickname, qr_code_url, phone, wx_number = map(g.json.get, ['wx_user_id', 'avatar', 'nickname',
                                                                                   'qr_code_url', 'phone', 'wx_number'])
    claim_args(1203, wx_user_id, avatar, nickname, qr_code_url, phone, wx_number)
    claim_args_int(1204, wx_user_id)
    claim_args_str(1204, avatar, nickname, qr_code_url, phone, wx_number)
    wx_user = WXUser.get_by_id(wx_user_id, code=1104)
    wx_user.update_info(avatar, nickname, phone, wx_number, qr_code_url)
    return api_success_response({})


@bp_user_api.route('/qn/upload_token/', methods=['POST'])
def get_open_upload_file_tokens():
    """
    获取上传文件至七牛云的token（无需验证）
    """

    # 需要上传的文件列表，形式为 [{'name':'1.jpg', 'type':0}, {'name':'2.mp4', 'type':1}]
    upload_list = g.json.get('upload_list')
    claim_args(1203, upload_list)
    claim_args_list(1204, upload_list)

    token_detail = KodoApi.get_file_upload_token(upload_list)
    data = {
        "token_detail": token_detail
    }
    return api_success_response(data)


@bp_user_api.route('/share/count/', methods=['GET'])
def count_share_times():
    """统计分享次数"""
    pass

