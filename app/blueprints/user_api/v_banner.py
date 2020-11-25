from . import bp_user_api
from ...api_utils import *
from ...models import Banner


@bp_user_api.route('/banner/', methods=['GET'])
def get_first_banner():
    """公众号网页首页获取banner图"""
    query = Banner.select().where(Banner.show == 1, Banner.is_delete == 0).order_by(Banner.weight.desc())

    data = {
        "banner": [banner.to_dict() for banner in query]
    }
    return api_success_response(data)

