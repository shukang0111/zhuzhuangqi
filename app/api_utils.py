from numbers import Number
import re

from flask import abort, current_app, g, jsonify, make_response, request, Response
from peewee import Query
from werkzeug.exceptions import HTTPException


__all__ = [
    'APIError',
    'handle_api_error',
    'handle_500_error',
    'handle_400_error',
    'handle_401_error',
    'handle_403_error',
    'handle_404_error',
    'before_api_request',
    'after_api_request',
    'api_success_response',
    'claim_args',
    'claim_args_true',
    'claim_args_bool',
    'claim_args_int',
    'claim_args_number',
    'claim_args_str',
    'claim_args_digit_str',
    'claim_args_list',
    'claim_args_dict',
    'claim_args_float',
    'paginate'
]


class APIError(Exception):
    """API错误"""
    # 错误码 & 错误描述
    ERRORS = {
        1000: 'Internal Server Error',
        1100: 'Bad Request',
        1101: 'Unauthorized',
        1102: 'Unauthorized',
        1103: 'Forbidden',
        1104: 'Not Found',
        1201: 'url参数不完整',
        1202: 'url参数值错误',
        1203: 'json数据不完整',
        1204: 'json数据类型错误',
        1205: 'json数据值错误',
        1206: '访问接口异常',
        1301: '用户名错误',
        1302: '密码错误',
        1303: '密码长度不符合要求',
        1304: '名称已存在',
        1305: '请添加二维码图片'
    }

    def __init__(self, code: int, message: str=None, status_code: int=200):
        """Initializer

        Args:
            code: 错误码
            message: 错误描述
            status_code: HTTP状态码
        """
        super().__init__()
        self.code = code
        self.message = message or self.ERRORS.get(code, 'Undefined')
        self.status_code = status_code

    def to_response(self) -> Response:
        """转换为flask.Response"""
        resp_data = {
            'code': self.code,
            'message': self.message,
            'data': {}
        }
        return make_response(jsonify(resp_data), self.status_code)


def handle_api_error(e: APIError) -> Response:
    """处理APIError"""
    return e.to_response()


def handle_500_error(e: HTTPException) -> Response:
    """处理500错误"""
    e = APIError(1000)
    return e.to_response()


def handle_400_error(e: HTTPException) -> Response:
    """处理400错误"""
    e = APIError(1100)
    return e.to_response()


def handle_401_error(e: HTTPException) -> Response:
    """处理401错误"""
    e = APIError(1101)
    return e.to_response()


def handle_403_error(e: HTTPException) -> Response:
    """处理403错误"""
    e = APIError(1103)
    return e.to_response()


def handle_404_error(e: HTTPException) -> Response:
    """处理404错误"""
    e = APIError(1104)
    return e.to_response()


def before_api_request() -> None:
    """API请求前钩子函数"""
    if request.method in ['POST', 'PUT']:
        try:
            g.json = request.get_json(force=True)  # g.json
        except Exception as e:
            current_app.logger.error(e)
            abort(400)
        else:
            current_app.logger.info('JSON -> {0}: {1}'.format(request.endpoint, g.json))


def after_api_request(resp):
    """api请求后勾子函数"""
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type, XMLHttpRequest, x-csrftoken'
    return resp

def api_success_response(data: object) -> object:
    """API请求成功的响应"""
    resp_data = {
        'code': 0,
        'message': 'Success',
        'data': data
    }
    return jsonify(resp_data)


def claim_args(code: int, *args, message: str=None) -> None:
    """如果args不都为真值或者Number，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not (a or isinstance(a, Number)):
            raise APIError(code, message)


def claim_args_true(code: int, *args, message: str = None) -> None:
    """如果args不都为真值，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not a:
            raise APIError(code, message)


def claim_args_bool(code: int, *args, message: str=None) -> None:
    """如果args不都为bool，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not isinstance(a, bool):
            raise APIError(code, message)


def claim_args_int(code: int, *args, message: str=None) -> None:
    """如果args不都为int，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not isinstance(a, int):
            raise APIError(code, message)


def claim_args_float(code: int, *args, message: str = None) -> None:
    """如果args不都为float,则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not isinstance(a, float):
            raise APIError(code, message)


def claim_args_number(code: int, *args, message: str=None) -> None:
    """如果args不都为Number，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not isinstance(a, Number):
            raise APIError(code, message)


def claim_args_str(code: int, *args, message: str=None) -> None:
    """如果args不都为str，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not isinstance(a, str):
            raise APIError(code, message)


# def claim_args_tone(code: int, *args, message: str=None) -> None:
#     """如果args不都为6位16进制字符串，则抛出APIError，则抛出APIError
#
#     Args:
#         code: APIError错误码
#         args: 参数列表
#         message: APIError错误描述
#     """
#     for a in args:
#         if not re.match(r'^[0-9A-F]{6}$', a):
#             raise APIError(code, message)


def claim_args_digit_str(code: int, *args, message: str=None) -> None:
    """如果args不都为数字字符串，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not (isinstance(a, str) and a.isdigit()):
            raise APIError(code, message)


def claim_args_list(code: int, *args, message: str=None) -> None:
    """如果args不都为list，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not isinstance(a, list):
            raise APIError(code, message)


def claim_args_dict(code: int, *args, message: str=None) -> None:
    """如果args不都为dict，则抛出APIError

    Args:
        code: APIError错误码
        args: 参数列表
        message: APIError错误描述
    """
    for a in args:
        if not isinstance(a, dict):
            raise APIError(code, message)


def paginate(query: Query) -> Query:
    """分页查询"""
    page, per_page = map(request.args.get, ['page', 'per_page'])
    try:
        page = int(page) if page else 0
        per_page = int(per_page) if per_page else 0
    except ValueError:
        pass
    else:
        if page > 0:
            if per_page > 0:
                return query.paginate(page, per_page)
            else:
                return query.paginate(page)
    return query
