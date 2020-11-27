from . import bp_user_api
from ...api_utils import *
from ...models import Course, Article


@bp_user_api.route('/course/list/', methods=['GET'])
def get_user_course_list():
    """查询课程list"""
    query = Course.select().where(Course.is_delete == 0, Course.show == 1).order_by(Course.weight.desc())
    _course = list()
    for course in query:
        item = course.to_dict()
        item['total_use_count'] = item['real_use_count'] + item['extra_add_count']
        _course.append(item)
    data = {
        "courses": _course
    }
    return api_success_response(data)


@bp_user_api.route('/course/detail/<int:course_id>/', methods=['GET'])
def get_user_course_detail(course_id):
    """查询单个课程详情"""
    course = Course.get_by_id(int(course_id), code=1104)
    item = course.to_dict()
    item['tid'] = 3
    item['cid'] = course.id
    data = {
        "course": item
    }
    return api_success_response(data)
