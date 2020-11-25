from . import bp_user_api
from ...api_utils import *
from ...models import Video


@bp_user_api.route('/video/list/', methods=['GET'])
def get_user_video_list():
    """查询视频list"""
    query = Video.select().where(Video.is_delete == 0, Video.show == 1).order_by(Video.weight.desc())
    _video = list()
    for video in query:
        item = video.to_dict()
        item['total_use_count'] = item['real_use_count'] + item['extra_add_count']
        _video.append(item)
    data = {
        "videos": _video
    }
    return api_success_response(data)


@bp_user_api.route('/video/detail/<int:video_id>/', methods=['GET'])
def get_user_video_detail(video_id):
    """查询单个视频详情"""
    video = Video.get_by_id(int(video_id), code=1104)
    data = {
        "video": video.to_dict()
    }
    return api_success_response(data)