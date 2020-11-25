from flask import g, request

from . import bp_admin_api
from ...api_utils import *
from ...models import Course


@bp_admin_api.route('/course/create/', methods=['POST'])
def create_course():
    """创建课程"""
    course_title, course_url, cover_url, extra_add_count = map(g.json.get, ['course_title', 'course_url', 'cover_url', 'extra_add_count'])
    claim_args(1203, course_title, course_url, cover_url, extra_add_count)
    claim_args_int(1204, extra_add_count)
    claim_args_str(1204, course_title, course_url, cover_url)
    Course.new(course_title, course_url, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/course/status/update/', methods=['POST'])
def update_course_status():
    """启用/停用课程"""
    course_id, show = map(g.json.get, ['course_id', 'show'])
    claim_args(1203, course_id, show)
    claim_args_int(1204, course_id, show)
    course = Course.get_by_id(course_id, code=1104)
    course.update_show(show)
    return api_success_response({})


@bp_admin_api.route('/course/delete/', methods=['POST'])
def delete_course():
    """删除课程"""
    course_id = g.json.get('course_id')
    claim_args_int(1204, course_id)
    course = Course.get_by_id(course_id, code=1104)
    course.update_delete(is_delete=1)
    return api_success_response({})


@bp_admin_api.route('/course/edit/', methods=['POST'])
def edit_course():
    """编辑课程"""
    course_id, course_title, course_url, cover_url, extra_add_count = map(g.json.get, ['course_id', 'course_title', 'course_url', 'cover_url', 'extra_add_count'])
    claim_args(1203, course_id, course_title, course_url, cover_url, extra_add_count)
    claim_args_int(1204, course_id, extra_add_count)
    claim_args_str(1204, course_title, course_url, cover_url)
    course = Course.get_by_id(course_id, code=1104)
    course.update_info(course_title, course_url, cover_url, extra_add_count)
    return api_success_response({})


@bp_admin_api.route('/course/list/', methods=['GET'])
def get_course_list():
    """查询课程list"""
    query = Course.select().where(Course.is_delete == 0)
    data = {
        "courses": [course.to_dict() for course in query]
    }
    return api_success_response(data)


@bp_admin_api.route('/course/detail/<int:course_id>/', methods=['GET'])
def get_course_detail(course_id):
    """查询单个课程详情"""
    course = Course.get_by_id(int(course_id), code=1104)
    data = {
        "course": course.to_dict()
    }
    return api_success_response(data)

