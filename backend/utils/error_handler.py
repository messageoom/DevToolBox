import logging
import traceback
from flask import jsonify

logger = logging.getLogger(__name__)

ERROR_MESSAGES = {
    'default': '操作失败，请稍后重试',
    'invalid_input': '输入参数无效',
    'file_not_found': '文件不存在',
    'file_too_large': '文件大小超出限制',
    'unsupported_type': '不支持的文件类型',
    'permission_denied': '权限不足',
}


def safe_error(e: Exception, user_message: str = None, status_code: int = 500):
    error_type = type(e).__name__
    error_msg = str(e)

    logger.error(f"[{error_type}] {error_msg}\n{traceback.format_exc()}")

    display_message = user_message or ERROR_MESSAGES.get('default')
    return jsonify({'error': display_message, 'success': False}), status_code
