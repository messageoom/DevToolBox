from flask import Blueprint, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import uuid

file_upload_bp = Blueprint('file_upload', __name__)

# 配置
ALLOWED_EXTENSIONS = {
    # 图片格式
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'ico',
    # 文档格式
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    # 数据格式
    'csv', 'json', 'xml',
    # 压缩文件
    'zip', 'rar', '7z',
    # 音频格式
    'mp3', 'mp4', 'avi', 'mov', 'wmv', 'flac', 'mflac', 'wav', 'aac', 'ogg',
    # 其他常见格式
    'exe', 'dll', 'iso', 'torrent'
}

def get_upload_folder():
    """获取上传文件夹路径"""
    # 优先使用Flask应用配置的UPLOAD_FOLDER
    from flask import current_app
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    
    # 如果没有配置，则使用默认路径
    if not upload_folder:
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
    
    # 确保存在上传目录
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    return upload_folder

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_upload_bp.route('/upload', methods=['POST'])
def upload_files():
    """上传文件"""
    try:
        # 获取上传文件夹路径
        UPLOAD_FOLDER = get_upload_folder()
        
        # 调试信息
        print("Received request files:", request.files)
        print("Request form:", request.form)
        print("Request method:", request.method)
        print("Content-Type:", request.content_type)
        print("Upload folder:", UPLOAD_FOLDER)

        # 检查是否有文件被提交
        if not request.files:
            return jsonify({'message': '成功上传 0 个文件', 'files': []}), 200

        # 获取所有上传的文件 - 直接使用getlist方法
        files = []
        try:
            files_list = request.files.getlist('files')
            if files_list:
                files = files_list
                print(f"Using getlist method, found {len(files)} files")
            else:
                print("getlist returned empty, trying alternative method")
                # 备选方法：遍历所有文件字段
                for key in request.files:
                    file_obj = request.files[key]
                    if hasattr(file_obj, 'filename') and file_obj.filename:
                        files.append(file_obj)
                print(f"Using alternative method, found {len(files)} files")
        except Exception as e:
            print(f"Error getting files with getlist: {e}")
            # 如果getlist失败，使用备选方法
            for key in request.files:
                file_obj = request.files[key]
                if hasattr(file_obj, 'filename') and file_obj.filename:
                    files.append(file_obj)
            print(f"Using fallback method, found {len(files)} files")

        print(f"Final file count: {len(files)}")
        for i, file in enumerate(files):
            print(f"File {i+1}: {file.filename if hasattr(file, 'filename') else 'No filename'}")

        # 如果没有有效文件
        if not files:
            return jsonify({'message': '成功上传 0 个文件', 'files': []}), 200

        uploaded_files = []
        max_files = 9

        # 限制文件数量
        if len(files) > max_files:
            files = files[:max_files]

        for file in files:
            try:
                if file and hasattr(file, 'filename') and file.filename:
                    # 保留原始文件名，包括中文和特殊字符
                    original_filename = file.filename
                    print(f"Processing file: {original_filename}")

                    # 手动清理文件名，只移除最危险的字符
                    # 保留中文字符、空格、常见符号，但移除路径相关的危险字符
                    import re
                    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', original_filename)

                    # 确保文件名不以点或空格开头或结尾
                    safe_filename = safe_filename.strip(' .')

                    # 如果清理后文件名为空，使用默认名称
                    if not safe_filename:
                        safe_filename = f"unnamed_file_{uuid.uuid4().hex[:8]}"

                    print(f"Safe filename: {safe_filename}")

                    # 处理没有扩展名的文件
                    if '.' not in safe_filename:
                        # 对于没有扩展名的文件，直接使用清理后的文件名
                        base_name = safe_filename
                        file_extension = ''
                        final_filename = base_name
                    else:
                        # 分离文件名和扩展名
                        parts = safe_filename.rsplit('.', 1)
                        if len(parts) == 2:
                            base_name = parts[0]
                            file_extension = parts[1].lower()

                            # 检查文件扩展名是否被允许
                            if file_extension not in ALLOWED_EXTENSIONS:
                                print(f"File extension {file_extension} not allowed")
                                continue
                        else:
                            base_name = safe_filename
                            file_extension = ''

                        final_filename = safe_filename

                    # 检查文件是否已存在，如果存在则添加数字后缀
                    counter = 1
                    temp_filename = final_filename
                    while os.path.exists(os.path.join(UPLOAD_FOLDER, temp_filename)):
                        if file_extension:
                            temp_filename = f"{base_name}_{counter}.{file_extension}"
                        else:
                            temp_filename = f"{base_name}_{counter}"
                        counter += 1

                    final_filename = temp_filename
                    file_path = os.path.join(UPLOAD_FOLDER, final_filename)
                    print(f"Saving to: {file_path}")

                    file.save(file_path)
                    file_size = os.path.getsize(file_path)

                    uploaded_files.append({
                        'original_name': original_filename,
                        'unique_name': final_filename,
                        'size': file_size,
                        'url': f'/api/file-upload/files/{final_filename}'
                    })

                    print(f"Successfully uploaded: {original_filename} -> {final_filename}")

            except Exception as file_error:
                print(f"Error processing file {file.filename}: {str(file_error)}")
                continue

        return jsonify({
            'message': f'成功上传 {len(uploaded_files)} 个文件',
            'files': uploaded_files
        }), 200

    except Exception as e:
        print("Upload error:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@file_upload_bp.route('/files', methods=['GET'])
def get_uploaded_files():
    """获取已上传的文件列表"""
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

        # 按修改时间倒序排序
        file_list.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({'files': file_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_upload_bp.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    """获取文件"""
    try:
        UPLOAD_FOLDER = get_upload_folder()
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        return jsonify({'error': '文件不存在'}), 404

@file_upload_bp.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """删除文件"""
    try:
        UPLOAD_FOLDER = get_upload_folder()
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': '文件删除成功'}), 200
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
