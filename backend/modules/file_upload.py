from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
import logging

try:
    from ..utils.path_safety import safe_join, sanitize_filename
    from ..utils.error_handler import safe_error
except ImportError:
    from backend.utils.path_safety import safe_join, sanitize_filename
    from backend.utils.error_handler import safe_error

logger = logging.getLogger(__name__)

file_upload_bp = Blueprint('file_upload', __name__)

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico',
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'csv', 'json', 'xml',
    'zip', 'rar', '7z',
    'mp3', 'mp4', 'avi', 'mov', 'wmv', 'flac', 'mflac', 'wav', 'aac', 'ogg',
}


def get_upload_folder():
    from flask import current_app
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@file_upload_bp.route('/upload', methods=['POST'])
def upload_files():
    try:
        UPLOAD_FOLDER = get_upload_folder()

        if not request.files:
            return jsonify({'message': '成功上传 0 个文件', 'files': []}), 200

        files = []
        try:
            files_list = request.files.getlist('files')
            if files_list:
                files = files_list
            else:
                for key in request.files:
                    file_obj = request.files[key]
                    if hasattr(file_obj, 'filename') and file_obj.filename:
                        files.append(file_obj)
        except Exception as e:
            logger.debug(f"Error getting files with getlist: {e}")
            for key in request.files:
                file_obj = request.files[key]
                if hasattr(file_obj, 'filename') and file_obj.filename:
                    files.append(file_obj)

        if not files:
            return jsonify({'message': '成功上传 0 个文件', 'files': []}), 200

        uploaded_files = []
        max_files = 9
        if len(files) > max_files:
            files = files[:max_files]

        for file in files:
            try:
                if file and hasattr(file, 'filename') and file.filename:
                    original_filename = file.filename
                    clean_name = sanitize_filename(original_filename)

                    if not clean_name or clean_name == 'unnamed_file':
                        clean_name = f"unnamed_file_{uuid.uuid4().hex[:8]}"

                    if '.' not in clean_name:
                        base_name = clean_name
                        file_extension = ''
                        final_filename = base_name
                    else:
                        parts = clean_name.rsplit('.', 1)
                        if len(parts) == 2:
                            base_name = parts[0]
                            file_extension = parts[1].lower()
                            if file_extension not in ALLOWED_EXTENSIONS:
                                logger.debug(f"File extension {file_extension} not allowed")
                                continue
                        else:
                            base_name = clean_name
                            file_extension = ''
                        final_filename = clean_name

                    counter = 1
                    temp_filename = final_filename
                    while os.path.exists(os.path.join(UPLOAD_FOLDER, temp_filename)):
                        if file_extension:
                            temp_filename = f"{base_name}_{counter}.{file_extension}"
                        else:
                            temp_filename = f"{base_name}_{counter}"
                        counter += 1

                    final_filename = temp_filename
                    file_path = safe_join(UPLOAD_FOLDER, final_filename)
                    if file_path is None:
                        logger.warning(f"Path traversal detected: {final_filename}")
                        continue

                    file.save(file_path)
                    file_size = os.path.getsize(file_path)

                    uploaded_files.append({
                        'original_name': original_filename,
                        'unique_name': final_filename,
                        'size': file_size,
                        'url': f'/api/file-upload/files/{final_filename}'
                    })

                    logger.debug(f"Successfully uploaded: {original_filename} -> {final_filename}")

            except Exception as file_error:
                logger.error(f"Error processing file: {file_error}")
                continue

        return jsonify({
            'message': f'成功上传 {len(uploaded_files)} 个文件',
            'files': uploaded_files
        }), 200

    except Exception as e:
        return safe_error(e, '文件上传失败')


@file_upload_bp.route('/files', methods=['GET'])
def get_uploaded_files():
    try:
        UPLOAD_FOLDER = get_upload_folder()
        files = os.listdir(UPLOAD_FOLDER)
        file_list = []

        for filename in files:
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file_stat = os.stat(file_path)
                file_list.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime,
                    'url': f'/api/file-upload/files/{filename}'
                })

        file_list.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify({'files': file_list}), 200

    except Exception as e:
        return safe_error(e, '获取文件列表失败')


@file_upload_bp.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    try:
        UPLOAD_FOLDER = get_upload_folder()
        safe_path = safe_join(UPLOAD_FOLDER, filename)
        if safe_path is None:
            return jsonify({'error': '无效的文件名'}), 400
        safe_name = sanitize_filename(filename)
        return send_from_directory(UPLOAD_FOLDER, safe_name)
    except Exception as e:
        return jsonify({'error': '文件不存在'}), 404


@file_upload_bp.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        UPLOAD_FOLDER = get_upload_folder()
        safe_path = safe_join(UPLOAD_FOLDER, filename)
        if safe_path is None:
            return jsonify({'error': '无效的文件名'}), 403
        if os.path.exists(safe_path):
            os.remove(safe_path)
            return jsonify({'message': '文件删除成功'}), 200
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return safe_error(e, '文件删除失败')
