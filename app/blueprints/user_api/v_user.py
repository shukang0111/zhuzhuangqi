from flask import request, g, current_app, redirect, session, render_template

from . import bp_user_api
from ...api_utils import *
from ...libs.kodo.kodo_api import KodoApi
from ...models import WXUser, Visitor, Share, Video, Article
from ...utils.calendar_util import calc_time
from ...utils.share_util import update_share_times
from ...utils.weixin_util import get_auth2_access_token, get_wx_user_detail, get_weixin_sign


@bp_user_api.route('/', methods=['GET'])
def index():
    """小程序回调"""

    code = request.args.get("code")
    current_app.logger.info(code)
    if code:
        item = get_auth2_access_token(code)
        access_token = item.get("access_token")
        openid = item.get("openid")
        current_app.logger.info("openid")
        user_info = get_wx_user_detail(access_token, openid)
        nickname = user_info.get("nickname").encode('iso-8859-1').decode('utf-8')
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
        session['openid'] = openid
        current_app.logger.info(openid)
        current_app.logger.info(request.referrer)

    # data = {
    #     "token": wx_user.gen_token()
    # }
    return redirect('https://zzqapi.e-shigong.com/')


@bp_user_api.route('/wx_user/', methods=['GET'])
def get_wx_user_center_info():
    """查询微信用户个人信息"""
    # wx_user = g.wx_user
    openid = session.get('openid')
    wx_user = WXUser.get_by_openid(openid)
    data = {
        "wx_user": wx_user.to_dict()
    }
    return api_success_response(data)


@bp_user_api.route('/wx_user/center/edit/', methods=['POST'])
def edit_wx_user_info():
    """个人中心信息更新"""
    wx_user_id, avatar, nickname, qr_code_url, phone, wx_number = map(g.json.get, ['wx_user_id', 'avatar', 'nickname',
                                                                                   'qr_code_url', 'phone', 'wx_number'])
    claim_args(1203, wx_user_id)
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


@bp_user_api.route('/weixin/js/auth/', methods=['GET'])
def get_weixin_ticket():
    """前端获取js配置信息"""
    # url = request.args.get('url')
    zzq_url = "https://zzqapi.e-shigong.com"
    url = request.full_path
    # wx_user = g.wx_user
    openid = session.get('openid')
    wx_user = WXUser.get_by_openid(openid)
    wx_url = zzq_url + url + '&oid=' + openid
    # wx_url = request.headers.get('Referer')
    current_app.logger.info(request.headers.get('Referer'))
    weixin_sign = get_weixin_sign(wx_url)
    weixin_sign['oid'] = wx_user.openid
    data = {
        "weixin_sign": weixin_sign
    }
    current_app.logger.info(data)
    return api_success_response(data)


@bp_user_api.route('/share/create/', methods=['POST'])
def create_share():
    """创建分享记录"""
    cid, tid = map(g.json.get, ['cid', 'tid'])
    # wx_user = g.wx_user
    openid = session.get('openid')
    wx_user = WXUser.get_by_openid(openid)
    Share.new(wx_user.id, tid, cid)
    return api_success_response({})


@bp_user_api.route('/share/count/', methods=['GET'])
def count_share_times():
    """用户点击分享链接"""
    current_app.logger.info(request.full_path)
    oid, cid, tid = map(request.args.get, ['oid', 'cid', 'tid'])
    # visitor_wx_user = g.wx_user
    openid = session.get('openid')
    visitor_wx_user = WXUser.get_by_openid(openid)
    share_wx_user = WXUser.get_by_openid(oid)
    try:
        share = Share.select().where(Share.wx_user_id == share_wx_user.id, Share.tid == int(tid), Share.cid == cid).get()
    except:
        pass
    else:
        share.update_real_use_count()
        Visitor.new(wx_user_id=share_wx_user.id, visitor_wx_user_id=visitor_wx_user.id, share_id=share.id)
    item = update_share_times(cid, tid)
    data = {
        "wx_user": share_wx_user.to_dict(),
        "info": item
    }
    return api_success_response(data)


@bp_user_api.route('/share/video/list/', methods=['GET'])
def get_user_share_video():
    """获取用户我的视频"""
    # wx_user = g.wx_user
    openid = session.get('openid')
    wx_user = WXUser.get_by_openid(openid)
    query = Share.select().where(Share.tid == 4, Share.wx_user_id == wx_user.id, Share.is_delete == 0)
    share_videos = list()
    # if not query.count():
    #     item = dict()
    #     _video = {
    #         "id": None,
    #         "video_title": '',
    #         "video_url": '',
    #         "cover_url": '',
    #         "real_use_count": None,
    #         "extra_add_count": None
    #     }
    #     item['video'] = _video
    #     share_videos.append(item)
    # else:
    for share in query:
        item = share.to_dict()
        video = Video.select().where(Video.id == share.cid).get()
        item['video'] = video.to_dict()
        item['total_use_count'] = share.real_use_count
        share_videos.append(item)
    data = {
        "videos": share_videos
    }
    return api_success_response(data)


@bp_user_api.route('/visitor/count/', methods=['GET'])
def visitor_count():
    """访客统计"""
    # wx_user = g.wx_user
    openid = session.get('openid')
    wx_user = WXUser.get_by_openid(openid)
    query = Visitor.select().where(Visitor.wx_user_id == wx_user.id).order_by(Visitor.visit_time.desc())

    _visitor = list()
    for visitor in query:
        item = visitor.to_dict()
        v_wx_user = WXUser.select().where(WXUser.id == visitor.visitor_wx_user_id).get()
        item['nickname'] = v_wx_user.nickname
        item['phone'] = v_wx_user.phone
        item['avatar'] = v_wx_user.avatar
        _visitor.append(item)
    total_count = query.count()
    start_time, end_time = calc_time("today")
    t_query = query.where(Visitor.visit_time.between(start_time, end_time))
    today_count = t_query.count()
    data = {
        "today_count": today_count,
        "total_count": total_count,
        "visitors": _visitor
    }
    return api_success_response(data)


@bp_user_api.route('/share/article/list/', methods=['GET'])
def get_user_share_article():
    """个人中心我的文章"""
    # wx_user = g.wx_user
    openid = session.get('openid')
    wx_user = WXUser.get_by_openid(openid)
    query = Share.select().where(Share.tid == 2, Share.wx_user_id == wx_user.id, Share.is_delete == 0)
    share_articles = list()
    # if not query.count():
    #     item = dict()
    #     _article = {
    #         "id": None,
    #         "article_type_id": None,
    #         "title": '',
    #         "contents": "'",
    #         "cover_url": '',
    #         "real_use_count": None,
    #         "extra_add_count": None
    #     }
    #     item['article'] = _article
    #     share_articles.append(item)
    # else:
    for share in query:
        item = share.to_dict()
        article = Article.select().where(Article.id == share.cid).get()
        item['article'] = article.to_dict()
        share_articles.append(item)
        item['total_use_count'] = share.real_use_count
    data = {
        "articles": share_articles
    }
    return api_success_response(data)


@bp_user_api.route('/share/delete/', methods=['POST'])
def delete_share_video():
    """删除个人中心我的视频/文章"""
    share_id = g.json.get("share_id")
    share = Share.get_by_id(share_id, code=1104)
    share.update_delete(is_delete=1)
    return api_success_response({})

