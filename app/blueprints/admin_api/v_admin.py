from flask import g, jsonify

from . import bp_admin_api
from ...api_utils import *
from ...libs.kodo.kodo_api import KodoApi
from ...models import Admin


@bp_admin_api.route('/admin/login/', methods=['POST'])
def login():
    """管理员登录"""
    username, password = map(g.json.get, ['username', 'password'])
    claim_args(1203, username, password)
    claim_args_str(1204, username, password)
    admin = Admin.get_by_username(username)
    claim_args_true(1301, admin)
    claim_args_true(1302, admin.check_password(password))

    data = {
        'token': admin.gen_token(),
        'admin': admin.to_dict()
    }
    return api_success_response(data)


@bp_admin_api.route('/current_admin/', methods=['GET'])
def get_current_admin():
    """获取当前管理员详情"""
    data = {
        'admin': g.admin.to_dict()
    }
    return api_success_response(data)


@bp_admin_api.route('/current_admin/password/', methods=['PUT'])
def update_current_admin_password():
    """修改当前管理员密码"""
    password = g.json.get('password')
    claim_args(1203, password)
    claim_args_str(1204, password)
    claim_args_true(1303, Admin.MIN_PW_LEN <= len(password) <= Admin.MAX_PW_LEN)

    g.admin.set_password(password)
    return api_success_response({})


# @bp_admin_api.route('/qn/upload_token/', methods=['GET'])
# def get_qn_upload_token():
#     """获取七牛上传token"""
#     data = {
#         'uptoken': qn_service.gen_upload_token()
#     }
#     return api_success_response(data)


@bp_admin_api.route('/qn/upload_token/', methods=['POST'])
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
