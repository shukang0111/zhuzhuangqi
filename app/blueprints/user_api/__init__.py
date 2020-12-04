from flask import Blueprint

from .hooks import user_authentication
from ...api_utils import *

bp_user_api = Blueprint('bp_user_api', __name__)
bp_user_api.register_error_handler(APIError, handle_api_error)
bp_user_api.register_error_handler(500, handle_500_error)
bp_user_api.register_error_handler(400, handle_400_error)
bp_user_api.register_error_handler(401, handle_401_error)
bp_user_api.register_error_handler(403, handle_403_error)
bp_user_api.register_error_handler(404, handle_404_error)
bp_user_api.before_request(before_api_request)
bp_user_api.before_request(user_authentication)
bp_user_api.after_request(after_api_request)

from . import v_user, v_video, v_course, v_article, v_poster, v_banner
