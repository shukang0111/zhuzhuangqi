from flask import request, g

from . import bp_admin_api
from ...api_utils import *
from ...models import Poster, PosterType


@bp_admin_api.route('/poster_type/create/', methods=['POST'])
def create_poster_type():
    """创建海报分类"""
    name = request.json.get("name")
    claim_args_str(1204, name)
    PosterType.new(name)
    return api_success_response({})


@bp_admin_api.route('/poster_type/edit/', methods=['POST'])
def edit_poster_type_name():
    """编辑海报分类名称"""
    poster_type_id, name = map(g.json.get, ['poster_type_id', 'name'])
    claim_args(1203, poster_type_id, name)
    claim_args_int(1204, poster_type_id)
    claim_args_str(1204, name)
    poster_type = PosterType.get_by_id(poster_type_id, code=1104)
    poster_type.update_name(name)
    return api_success_response({})


@bp_admin_api.route('/poster_type/delete/', methods=['POST'])
def delete_poster_type():
    """删除海报分类"""
    poster_type_id = g.json.get("poster_type_id")
    claim_args_int(1204, poster_type_id)
    poster_type = PosterType.get_by_id(poster_type_id, code=1104)
    query = Poster.select().where(Poster.poster_type_id == poster_type_id)
    for poster in query:
        poster.update_delete(is_delete=1)
    poster_type.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/poster_type/all/', methods=['GET'])
def get_all_poster_type():
    """查询所有海报分类"""
    query = PosterType.select().where(PosterType.is_delete == 0)
    data = {
        "poster_types": [poster_type.to_dict() for poster_type in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/poster/create/', methods=['POST'])
def create_poster():
    """创建海报"""
    poster_type_id, name, cover_url, extra_add_count = map(g.json.get, ['poster_type_id', 'name', 'cover_url', 'extra_add_count'])
    claim_args(1203, poster_type_id, name, cover_url)
    claim_args_int(1204, poster_type_id)
    claim_args_str(1204, name, cover_url)

    Poster.new(poster_type_id, name, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/poster/status/update/', methods=['POST'])
def update_poster_status():
    """海报启用/停用"""
    poster_id, show = map(g.json.get, ['poster_id', 'show'])
    claim_args(1203, poster_id, show)
    claim_args_int(1204, poster_id, show)
    poster = Poster.get_by_id(poster_id, code=1104)
    poster.update_show(show)
    return api_success_response({})


@bp_admin_api.route('/poster/delete/', methods=['POST'])
def delete_poster():
    """删除海报"""
    poster_id = g.json.get('poster_id')
    claim_args_int(1204, poster_id)
    poster = Poster.get_by_id(poster_id, code=1104)
    poster.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/poster/edit/', methods=['POST'])
def edit_poster():
    """编辑单个海报"""
    poster_id, name, cover_url, extra_add_count = map(g.json.get, ['poster_id', 'name', 'cover_url', 'extra_add_count'])
    claim_args(1203, poster_id, name, cover_url, extra_add_count)
    claim_args_int(1204, poster_id, extra_add_count)
    claim_args_str(1204, name, cover_url)
    check_poster = Poster.get_by_name(name)
    if check_poster:
        if check_poster.id == poster_id:
            raise APIError(1304)
    poster = Poster.get_by_id(poster_id, code=1104)
    poster.name = name
    poster.cover_url = cover_url
    poster.extra_add_count = extra_add_count
    poster.save_ut()
    return api_success_response({})


@bp_admin_api.route('/poster/list/<int:poster_type_id>/', methods=['GET'])
def get_poster_list(poster_type_id):
    """获取单个海报类型下的海报列表"""
    poster_type = PosterType.get_by_id(poster_type_id, code=1104)
    _poster_type = poster_type.to_dict()
    _posters = list()
    posters = Poster.select().where(Poster.poster_type_id == poster_type.id, Poster.is_delete == 0)
    for poster in posters:
        _posters.append(poster.to_dict())
    _poster_type["poster"] = _posters

    data = {
        "poster_list": _poster_type
    }
    return api_success_response(data)


@bp_admin_api.route('/poster/detail/<int:poster_id>/', methods=['GET'])
def get_poster_detail(poster_id):
    """获取单个海报详情"""
    # poster_id = request.args.get("poster_id")
    poster = Poster.get_by_id(int(poster_id), code=1104)
    data = {
        "poster": poster.to_dict()
    }
    return api_success_response(data)
