from flask import abort, g, request

from ...models import Admin


def admin_auth() -> None:
    """管理员身份认证"""
    if request.endpoint.split('.')[-1] in ['login', 'get_open_upload_file_tokens']:
        return
    # token = request.headers.get('Authorization')
    # if token:
    #     admin = Admin.get_by_token(token)
    #     if admin:
    #         g.admin = admin  # g.admin
    #         return
    # abort(401)
