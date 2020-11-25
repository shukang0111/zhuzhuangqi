from flask import g, request

from . import bp_admin_api
from ...api_utils import *
from ...models import Banner


@bp_admin_api.route('/banner/create/', methods=['POST'])
def create_banner():
    """创建banner图"""
    cover_url, jump_url = map(g.json.get, ['cover_url', 'jump_url'])
    claim_args(1203, cover_url, jump_url)
    claim_args_str(1204, cover_url, jump_url)
    Banner.new(cover_url, jump_url)
    return api_success_response({})


@bp_admin_api.route('/banner/status/update/', methods=['POST'])
def update_banner_status():
    """启用/停用banner图"""
    banner_id, show = map(g.json.get, ['banner_id', 'show'])
    claim_args(1203, banner_id, show)
    claim_args_int(1204, banner_id, show)
    banner = Banner.get_by_id(banner_id, code=1104)
    banner.update_show(show)
    return api_success_response({})


@bp_admin_api.route('/banner/delete/', methods=['POST'])
def delete_banner():
    """删除banner图"""
    banner_id = g.json.get('banner_id')
    banner = Banner.get_by_id(banner_id, code=1104)
    banner.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/banner/edit/', methods=['POST'])
def edit_banner():
    """编辑banner图"""
    banner_id, cover_url, jump_url = map(g.json.get, ['banner_id', 'cover_url', 'jump_url'])
    claim_args(1203, banner_id, cover_url, jump_url)
    claim_args_int(1204, banner_id)
    claim_args_str(1204, cover_url, jump_url)
    banner = Banner.get_by_id(banner_id, code=1104)
    banner.update_info(cover_url, jump_url)
    return api_success_response({})


@bp_admin_api.route('/banner/list/', methods=['GET'])
def get_banner_list():
    """查询banner图list"""
    query = Banner.select().where(Banner.is_delete == 0)
    data = {
        "banners": [banner.to_dict() for banner in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/banner/detail/<int:banner_id>/', methods=['GET'])
def get_banner_detail(banner_id):
    """查询单个banner图详情"""
    # banner_id = request.args.get("banner_id")
    banner = Banner.get_by_id(int(banner_id), code=1104)
    data = {
        "banner": banner.to_dict()
    }
    return api_success_response(data)

