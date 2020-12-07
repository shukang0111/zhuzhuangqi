from flask import g, session

from . import bp_user_api
from ...api_utils import *
from ...models import PosterType, Poster, PosterTheme, WXUser


@bp_user_api.route('/poster_type/all/', methods=['GET'])
def get_all_poster_type():
    """查询所有海报分类"""
    query = PosterType.select().where(PosterType.is_delete == 0)
    data = {
        "poster_types": [poster_type.to_dict() for poster_type in query]
    }
    return api_success_response(data)


@bp_user_api.route('/poster/list/<int:poster_type_id>/', methods=['GET'])
def get_user_poster_list(poster_type_id):
    """公众号页面海报列表"""
    poster_type = PosterType.get_by_id(poster_type_id, code=1104)
    _poster_type = poster_type.to_dict()
    _posters = list()
    posters = Poster.select().where(Poster.poster_type_id == poster_type.id, Poster.is_delete == 0)
    for poster in posters:
        item = poster.to_dict()
        item['total_use_count'] = item['real_use_count'] + item['extra_add_count']
        _posters.append(item)
    _poster_type["poster"] = _posters

    data = {
        "poster_list": _poster_type
    }

    return api_success_response(data)


@bp_user_api.route('/poster/detail/<int:poster_id>/', methods=['GET'])
def get_user_poster_detail(poster_id):
    """公众号单个海报详情"""
    poster = Poster.get_by_id(poster_id, code=1104)
    item = poster.to_dict()
    item['tid'] = 1
    item['cid'] = poster.id
    data = {
        "poster": item
    }
    return api_success_response(data)


@bp_user_api.route('/poster_theme/list/', methods=['GET'])
def get_user_poster_theme_list():
    """微信个人海报列表"""
    # openid = session.get("openid")
    # wx_user = WXUser.get_by_openid(openid)
    wx_user = g.wx_user
    query = PosterTheme.select().where(PosterTheme.wx_user_id == wx_user.id, PosterTheme.is_delete == 0).\
        order_by(PosterTheme.weight.desc())
    _poster_thmes = list()
    for poster_theme in query:
        item = poster_theme.to_dict()
        item['total_use_count'] = item['real_use_count'] + item['extra_add_count']
        _poster_thmes.append(item)
    data = {
        "poster_themes": _poster_thmes
    }
    return api_success_response(data)


@bp_user_api.route('/poster_theme/create/', methods=['POST'])
def create_poster_theme():
    """创建我的海报"""
    wx_user_id, poster_id, cover_url = map(g.json.get, ['wx_user_id', 'poster_id', 'cover_url'])
    claim_args(1203, wx_user_id, poster_id,)
    claim_args_int(1204, wx_user_id, poster_id)
    if not cover_url:
        raise APIError(1305)
    poster = Poster.get_by_id(poster_id, code=1104)
    name = poster.name
    real_use_count = poster.real_use_count
    extra_add_count = poster.extra_add_count
    poster_theme = PosterTheme.new(wx_user_id, poster_id, name, cover_url)
    poster_theme.real_use_count = real_use_count
    poster_theme.extra_add_count = extra_add_count
    poster_theme.save_ut()
    return api_success_response({})


@bp_user_api.route('/poster_theme/name/update/', methods=['POST'])
def update_poster_theme_name():
    """更新我的海报名称"""
    poster_theme_id, name = map(g.json.get, ['poster_theme_id', 'name'])
    claim_args(1203, poster_theme_id, name)
    claim_args_int(1204, poster_theme_id)
    claim_args_str(1204, name)
    poster_theme = PosterTheme.get_by_id(poster_theme_id, code=1104)
    poster_theme.update_name(name)
    return api_success_response({})


@bp_user_api.route('/poster_theme/delete/', methods=['POST'])
def delete_poster_theme():
    """删除我的海报"""
    poster_theme_id = g.json.get("poster_theme_id")
    poster_theme = PosterTheme.get_by_id(poster_theme_id, code=1104)
    poster_theme.update_delete(is_delete=1)
    return api_success_response({})
