from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid
import logging
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

try:
    from ..utils.path_safety import safe_join, sanitize_filename
    from ..utils.error_handler import safe_error
except ImportError:
    try:
        from backend.utils.path_safety import safe_join, sanitize_filename
        from backend.utils.error_handler import safe_error
    except ImportError:
        from utils.path_safety import safe_join, sanitize_filename
        from utils.error_handler import safe_error

logger = logging.getLogger(__name__)

file_upload_bp = Blueprint('file_upload', __name__)

try:
    import fitz
except ImportError:
    fitz = None

# Executable file extensions that may pose security risks
EXECUTABLE_EXTENSIONS = {
    'exe', 'bat', 'cmd', 'ps1', 'vbs', 'vbe', 'js', 'jse', 'wsf', 'wsh',
    'msi', 'msp', 'mst', 'cpl', 'dll', 'scr', 'pif', 'com',
    'sh', 'bash', 'zsh', 'fish',
    'py', 'rb', 'pl', 'php',
}

EBOOK_EXTENSIONS = {'epub'}


def get_upload_folder():
    from flask import current_app
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        try:
            from utils.config_manager import load_config, get_upload_dir
        except ImportError:
            try:
                from backend.utils.config_manager import load_config, get_upload_dir
            except ImportError:
                load_config = get_upload_dir = None
        if load_config and get_upload_dir:
            upload_folder = get_upload_dir(load_config())
    if not upload_folder:
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder


def scan_file(filepath):
    """Basic file safety scan.
    Returns a dict with 'safe' (bool) and 'warning' (str or None).
    """
    ext = filepath.rsplit('.', 1)[-1].lower() if '.' in filepath else ''

    # Warn about executable files
    if ext in EXECUTABLE_EXTENSIONS:
        return {'safe': True, 'warning': f'Executable file (.{ext}) uploaded — handle with caution'}

    # On Windows, try Windows Defender quick scan for files under 500MB
    if sys.platform == 'win32':
        try:
            file_size = os.path.getsize(filepath)
            if file_size < 500 * 1024 * 1024:
                mp_cmd = r'C:\Program Files\Windows Defender\MpCmdRun.exe'
                if os.path.exists(mp_cmd):
                    result = subprocess.run(
                        [mp_cmd, '-Scan', '-ScanType', '3', '-File', filepath],
                        capture_output=True, timeout=60,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                    if result.returncode == 2:
                        return {'safe': False, 'warning': 'Threat detected by Windows Defender'}
        except Exception:
            pass

    return {'safe': True, 'warning': None}


# --- Ebook metadata extraction ---

_EPUB_NS = {
    'container': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'opf': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/',
}


def get_covers_folder(upload_folder):
    covers_dir = os.path.join(upload_folder, '_covers')
    os.makedirs(covers_dir, exist_ok=True)
    return covers_dir


def cover_cache_path(upload_folder, filename):
    safe = sanitize_filename(filename)
    return os.path.join(get_covers_folder(upload_folder), safe + '.png')


def extract_epub_metadata(filepath):
    """Extract title and cover image bytes from an EPUB file."""
    result = {'title': None, 'cover_bytes': None}
    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            container_xml = zf.read('META-INF/container.xml')
            container_root = ET.fromstring(container_xml)
            opf_path = container_root.find(
                './/container:rootfile', _EPUB_NS
            ).attrib.get('full-path', '')
            if not opf_path:
                return result

            opf_xml = zf.read(opf_path)
            opf_root = ET.fromstring(opf_xml)

            title_el = opf_root.find('.//dc:title', _EPUB_NS)
            if title_el is not None and title_el.text:
                result['title'] = title_el.text.strip()

            cover_id = None
            for meta in opf_root.findall('.//opf:meta', _EPUB_NS):
                if meta.attrib.get('name') == 'cover':
                    cover_id = meta.attrib.get('content')
                    break

            cover_href = None
            manifest_items = {}
            for item in opf_root.findall('.//opf:manifest/opf:item', _EPUB_NS):
                item_id = item.attrib.get('id', '')
                href = item.attrib.get('href', '')
                properties = item.attrib.get('properties', '')
                manifest_items[item_id] = href
                if 'cover-image' in properties:
                    cover_href = href

            if cover_id and cover_id in manifest_items:
                cover_href = manifest_items[cover_id]

            if not cover_href:
                return result

            opf_dir = os.path.dirname(opf_path)
            cover_zip_path = os.path.join(opf_dir, cover_href).replace('\\', '/') if opf_dir else cover_href

            names = zf.namelist()
            if cover_zip_path in names:
                result['cover_bytes'] = zf.read(cover_zip_path)
            else:
                lower_map = {n.lower(): n for n in names}
                if cover_zip_path.lower() in lower_map:
                    result['cover_bytes'] = zf.read(lower_map[cover_zip_path.lower()])
    except Exception as e:
        logger.debug(f"EPUB metadata extraction failed for {filepath}: {e}")

    return result


def extract_pdf_cover(filepath):
    """Render first page of a PDF as PNG bytes using PyMuPDF."""
    if fitz is None:
        return None
    try:
        doc = fitz.open(filepath)
        if len(doc) == 0:
            doc.close()
            return None
        page = doc[0]
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat)
        png_bytes = pix.tobytes('png')
        doc.close()
        return png_bytes
    except Exception as e:
        logger.debug(f"PDF cover extraction failed for {filepath}: {e}")
        return None


def get_ebook_metadata(upload_folder, filename):
    """Get ebook metadata (title, coverUrl) for a file. Uses cached cover if available."""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    is_epub = ext == 'epub'
    is_pdf = ext == 'pdf'

    if not is_epub and not is_pdf:
        return {'title': None, 'coverUrl': None}

    cache_png = cover_cache_path(upload_folder, filename)
    cover_url = None
    title = None

    if os.path.exists(cache_png):
        cover_url = f'/api/file-upload/files/{filename}/cover'
    else:
        cover_bytes = None
        filepath = os.path.join(upload_folder, filename)
        if is_epub:
            meta = extract_epub_metadata(filepath)
            title = meta['title']
            cover_bytes = meta['cover_bytes']
        elif is_pdf:
            cover_bytes = extract_pdf_cover(filepath)

        if cover_bytes:
            os.makedirs(os.path.dirname(cache_png), exist_ok=True)
            with open(cache_png, 'wb') as f:
                f.write(cover_bytes)
            cover_url = f'/api/file-upload/files/{filename}/cover'

    if is_epub and title is None:
        filepath = os.path.join(upload_folder, filename)
        meta = extract_epub_metadata(filepath)
        title = meta['title']

    return {'title': title, 'coverUrl': cover_url}
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
            logger.debug(f"Error getting files: {e}")
            for key in request.files:
                file_obj = request.files[key]
                if hasattr(file_obj, 'filename') and file_obj.filename:
                    files.append(file_obj)

        if not files:
            return jsonify({'message': '成功上传 0 个文件', 'files': []}), 200

        uploaded_files = []
        warnings = []
        if len(files) > 9:
            files = files[:9]

        for file in files:
            try:
                if file and hasattr(file, 'filename') and file.filename:
                    original_filename = file.filename
                    clean_name = sanitize_filename(original_filename)

                    if not clean_name or clean_name == 'unnamed_file':
                        clean_name = f"unnamed_file_{uuid.uuid4().hex[:8]}"

                    # Handle duplicate filenames
                    if '.' in clean_name:
                        parts = clean_name.rsplit('.', 1)
                        base_name, file_extension = parts[0], parts[1].lower()
                    else:
                        base_name = clean_name
                        file_extension = ''

                    final_filename = clean_name
                    counter = 1
                    while os.path.exists(os.path.join(UPLOAD_FOLDER, final_filename)):
                        if file_extension:
                            final_filename = f"{base_name}_{counter}.{file_extension}"
                        else:
                            final_filename = f"{base_name}_{counter}"
                        counter += 1

                    file_path = safe_join(UPLOAD_FOLDER, final_filename)
                    if file_path is None:
                        logger.warning(f"Path traversal detected: {final_filename}")
                        continue

                    file.save(file_path)
                    file_size = os.path.getsize(file_path)

                    # Safety scan
                    scan_result = scan_file(file_path)
                    if not scan_result['safe']:
                        os.remove(file_path)
                        warnings.append(f"{final_filename}: {scan_result['warning']}")
                        logger.warning(f"Blocked unsafe file: {final_filename} - {scan_result['warning']}")
                        continue
                    if scan_result['warning']:
                        warnings.append(f"{final_filename}: {scan_result['warning']}")

                    uploaded_files.append({
                        'original_name': original_filename,
                        'unique_name': final_filename,
                        'size': file_size,
                        'url': f'/api/file-upload/files/{final_filename}'
                    })

            except Exception as file_error:
                logger.error(f"Error processing file: {file_error}")
                continue

        response = {
            'message': f'成功上传 {len(uploaded_files)} 个文件',
            'files': uploaded_files,
        }
        if warnings:
            response['warnings'] = warnings
        return jsonify(response), 200

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
                file_entry = {
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime,
                    'url': f'/api/file-upload/files/{filename}'
                }

                ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
                if ext in EBOOK_EXTENSIONS or ext == 'pdf':
                    try:
                        ebook_meta = get_ebook_metadata(UPLOAD_FOLDER, filename)
                        if ebook_meta.get('coverUrl'):
                            file_entry['coverUrl'] = ebook_meta['coverUrl']
                        if ebook_meta.get('title'):
                            file_entry['title'] = ebook_meta['title']
                    except Exception as e:
                        logger.debug(f"Ebook metadata enrichment failed for {filename}: {e}")

                file_list.append(file_entry)

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
    except Exception:
        return jsonify({'error': '文件不存在'}), 404


@file_upload_bp.route('/files/<filename>/cover', methods=['GET'])
def get_file_cover(filename):
    try:
        UPLOAD_FOLDER = get_upload_folder()
        safe_path = safe_join(UPLOAD_FOLDER, filename)
        if safe_path is None:
            return jsonify({'error': '无效的文件名'}), 400

        cache_png = cover_cache_path(UPLOAD_FOLDER, filename)
        if not os.path.exists(cache_png):
            return jsonify({'error': 'No cover available'}), 404

        covers_dir = os.path.dirname(cache_png)
        cover_filename = os.path.basename(cache_png)
        return send_from_directory(covers_dir, cover_filename)
    except Exception:
        return jsonify({'error': 'Cover not found'}), 404


@file_upload_bp.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        UPLOAD_FOLDER = get_upload_folder()
        safe_path = safe_join(UPLOAD_FOLDER, filename)
        if safe_path is None:
            return jsonify({'error': '无效的文件名'}), 403
        if os.path.exists(safe_path):
            os.remove(safe_path)
            cache_png = cover_cache_path(UPLOAD_FOLDER, filename)
            if os.path.exists(cache_png):
                try:
                    os.remove(cache_png)
                except OSError:
                    pass
            return jsonify({'message': '文件删除成功'}), 200
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return safe_error(e, '文件删除失败')
