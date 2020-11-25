from flask import g, request

from . import bp_admin_api
from ...api_utils import *
from ...models import Video


@bp_admin_api.route('/video/create/', methods=['POST'])
def create_video():
    """创建视频"""
    video_title, video_url, cover_url, extra_add_count = map(g.json.get, ['video_title', 'video_url', 'cover_url', 'extra_add_count'])
    claim_args(1203, video_title, video_url, cover_url, extra_add_count)
    claim_args_int(1204, extra_add_count)
    claim_args_str(1204, video_title, video_url, cover_url)
    Video.new(video_title, video_url, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/video/status/update/', methods=['POST'])
def update_video_status():
    """启用/停用视频"""
    video_id, show = map(g.json.get, ['video_id', 'show'])
    claim_args(1203, video_id, show)
    claim_args_int(1204, video_id, show)
    video = Video.get_by_id(video_id, code=1104)
    video.update_show(show)
    return api_success_response({})


@bp_admin_api.route('/video/delete/', methods=['POST'])
def delete_video():
    """删除课程"""
    video_id = g.json.get('video_id')
    claim_args_int(1204, video_id)
    video = Video.get_by_id(video_id, code=1104)
    video.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/video/edit/', methods=['POST'])
def edit_video():
    """编辑视频"""
    video_id, video_title, video_url, cover_url, extra_add_count = map(g.json.get, ['video_id', 'video_title', 'video_url', 'cover_url', 'extra_add_count'])
    claim_args(1203, video_id, video_title, video_url, cover_url, extra_add_count)
    claim_args_int(1204, video_id, extra_add_count)
    claim_args_str(1204, cover_url, video_title, video_url, cover_url)
    video = Video.get_by_id(video_id, code=1104)
    video.update_info(video_title, video_url, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/video/list/', methods=['GET'])
def get_video_list():
    """查询视频list"""
    query = Video.select().where(Video.is_delete == 0)
    data = {
        "videos": [video.to_dict() for video in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/video/detail/<int:video_id>/', methods=['GET'])
def get_video_detail(video_id):
    """查询单个视频详情"""
    video = Video.get_by_id(int(video_id), code=1104)
    data = {
        "video": video.to_dict()
    }
    return api_success_response(data)

