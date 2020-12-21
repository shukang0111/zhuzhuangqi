from flask import request

from . import bp_user_api
from ...api_utils import *
from ...models import Area


@bp_user_api.route('/area/first/info/', methods=['GET'])
def get_area_first_info():
    """获取一级地区信息"""
    query = Area.select().where(Area.pid == 0)
    area_list = [item.to_dict() for item in query]
    data = {
        'area_list': area_list
    }
    return api_success_response(data)


@bp_user_api.route('/area/second/info/', methods=['GET'])
def get_area_second_info():
    """获取二/三级地区信息"""
    area_id = request.args.get('area_id')
    area = Area.get_by_id(area_id, code=1104)
    query = Area.select().where(Area.pid == area)
    area_list = [item.to_dict() for item in query]
    data = {
        'area_list': area_list
    }
    return api_success_response(data)
