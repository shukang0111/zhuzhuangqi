from flask import request, g, current_app, redirect, session, render_template

from . import bp_user_api
from ...api_utils import *
from ...libs.kodo.kodo_api import KodoApi
from ...models import WXUser, Visitor, Share, Video, Article, ArticleType, db
from ...utils.calendar_util import calc_time
from ...utils.common_util import get_detail_area_info
from ...utils.re_util import check_mobile
from ...utils.share_util import update_share_times
from ...utils.weixin_util import get_auth2_access_token, get_wx_user_detail, get_weixin_sign


@bp_user_api.route('/', methods=['GET'])
def index():
    """授权回调"""

    code = request.args.get("code")
    current_app.logger.info(code)
    # if code:
    item = get_auth2_access_token(code)
    access_token = item.get("access_token")
    openid = item.get("openid")
    user_info = get_wx_user_detail(access_token, openid)
    current_app.logger.info(user_info)
    nickname = user_info.get("nickname")
    if nickname:
        nickname = nickname.encode('iso-8859-1').decode('utf-8')
    headimgurl = user_info.get("headimgurl")
    try:
        wx_user = WXUser.get_by_openid(openid)
        wx_user.nickname = nickname
        wx_user.avatar = headimgurl
        wx_user.save()
    except Exception as e:
        current_app.logger.error(e)
        wx_user = WXUser.new(openid, headimgurl, nickname)
        wx_user.article_types.clear()
        query = ArticleType.select().where(ArticleType.is_delete == 0, ArticleType.show == 1)
        wx_user.article_types.add(query)
    data = {
        "token": wx_user.gen_token()
    }
    return api_success_response(data)


@bp_user_api.route('/wx_user/', methods=['GET'])
def get_wx_user_center_info():
    """查询微信用户个人信息"""
    wx_user = g.wx_user
    item = wx_user.to_dict()
    if wx_user.area_info_id:
        item['detail_address'] = get_detail_area_info(wx_user.area_info_id)
    else:
        item['detail_address'] = None
    data = {
        "wx_user": item
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
    wx_user = g.wx_user
    # openid = session.get('openid')
    # wx_user = WXUser.get_by_openid(openid)
    # wx_url = zzq_url + url
    wx_url = request.headers.get('Referer')
    # current_app.logger.info(request.headers.get('Referer'))
    # current_app.logger.info('wx_url')
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
    wx_user = g.wx_user
    # openid = session.get('openid')
    # wx_user = WXUser.get_by_openid(openid)
    Share.new(wx_user.id, tid, cid)
    return api_success_response({})


@bp_user_api.route('/share/count/', methods=['GET'])
def count_share_times():
    """用户点击分享链接"""
    current_app.logger.info(request.full_path)
    oid, cid, tid = map(request.args.get, ['oid', 'cid', 'tid'])
    visitor_wx_user = g.wx_user
    # openid = session.get('openid')
    # visitor_wx_user = WXUser.get_by_openid(openid)
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
    wx_user = g.wx_user
    query = Share.select().where(Share.tid == 4, Share.wx_user_id == wx_user.id, Share.is_delete == 0)
    share_videos = list()
    share_video_ids = list()
    for share in query:
        item = share.to_dict()
        video = Video.select().where(Video.id == share.cid).get()
        if video.id in share_video_ids:
            continue
        item['video'] = video.to_dict()
        item['total_use_count'] = share.real_use_count
        share_videos.append(item)
        share_video_ids.append(video.id)
    data = {
        "videos": share_videos
    }
    return api_success_response(data)


@bp_user_api.route('/visitor/count/', methods=['GET'])
def visitor_count():
    """访客统计"""
    wx_user = g.wx_user
    query = Visitor.select().where(Visitor.wx_user_id == wx_user.id).order_by(Visitor.visit_time.desc())
    start_time, end_time = calc_time("today")
    _visitor = list()
    _visitor_user_ids = list()
    _today_visitor_user_ids = list()
    for visitor in query:
        item = visitor.to_dict()
        v_wx_user = WXUser.select().where(WXUser.id == visitor.visitor_wx_user_id).get()
        if v_wx_user.id in _visitor_user_ids:
            continue
        item['nickname'] = v_wx_user.nickname
        item['phone'] = v_wx_user.phone
        item['avatar'] = v_wx_user.avatar
        item['room_size'] = v_wx_user.room_size
        if v_wx_user.area_info_id:
            item['detail_address'] = get_detail_area_info(v_wx_user.area_info_id)
        else:
            item['detail_address'] = None
        _visitor.append(item)
        _visitor_user_ids.append(v_wx_user.id)
        # 今日访客记录
        if start_time < visitor.visit_time < end_time:
            _today_visitor_user_ids.append(v_wx_user.id)
    total_count = len(_visitor_user_ids)
    today_count = len(_today_visitor_user_ids)
    data = {
        "today_count": today_count,
        "total_count": total_count,
        "visitors": _visitor
    }
    return api_success_response(data)


@bp_user_api.route('/share/article/list/', methods=['GET'])
def get_user_share_article():
    """个人中心我的文章"""
    wx_user = g.wx_user
    query = Share.select().where(Share.tid == 2, Share.wx_user_id == wx_user.id, Share.is_delete == 0)
    share_articles = list()
    share_article_ids = list()
    for share in query:
        item = share.to_dict()
        current_app.logger.info('share_cid:{}'.format(share.cid))
        article = Article.select().where(Article.id == share.cid).get()
        if article.id in share_article_ids:
            continue
        item['article'] = article.to_dict()
        share_articles.append(item)
        share_article_ids.append(article.id)
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


@bp_user_api.route('/wx_user/article_types/', methods=['GET'])
def get_user_article_types():
    """查询用户选择文章类型"""
    user = g.wx_user
    article_types = list()
    for article_type in user.article_types:
        article_types.append(article_type.to_dict())

    data = {
        "article_types": article_types
    }
    return api_success_response(data)


@bp_user_api.route('/wx_user/article_types/create/', methods=['POST'])
def create_wx_user_article_types():
    """用户订阅专属文章类型"""
    article_type_ids = g.json.get("article_type_ids")
    claim_args_list(1204, article_type_ids)
    user = g.wx_user
    with db.atomic():
        user.article_types.clear()
        query = ArticleType.select().where(ArticleType.id.in_(article_type_ids), ArticleType.is_delete == 0, ArticleType.show == 1)
        user.article_types.add(query)
    return api_success_response({})


@bp_user_api.route('/wx_user/brand/create/', methods=['POST'])
def create_wx_user_brand():
    """用户填写品牌名称"""
    brand = g.json.get('brand')
    user = g.wx_user
    if brand:
        user.brand = brand
        user.save_ut()
    return api_success_response({})


@bp_user_api.route('/room_decoration/', methods=['POST'])
def update_user_room_info():
    """
    用户获取装修报价
    :return:
    """
    area_info_id, nickname, phone, room_size = map(g.json.get, ['area_info_id', 'nickname', 'phone', 'room_size'])
    if not area_info_id:
        raise APIError(1306)
    if not nickname:
        raise APIError(1307)
    if not phone:
        raise APIError(1308)
    if not check_mobile(phone):
        raise APIError(1310)
    if not room_size:
        raise APIError(1309)
    claim_args_str(1204, nickname, phone)
    claim_args_number(1204, area_info_id, room_size)
    wx_user = g.wx_user
    wx_user.area_info_id = area_info_id
    wx_user.nickname = nickname
    wx_user.phone = phone
    wx_user.room_size = room_size
    wx_user.save()
    return api_success_response({})
