from flask import Blueprint, request, jsonify, send_file
import html2text
import os
import tempfile
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF for PDF processing
from bs4 import BeautifulSoup
import re
import logging

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

try:
    from .data_conversion_styles import build_full_html, build_preview_html
except ImportError:
    from data_conversion_styles import build_full_html, build_preview_html

logger = logging.getLogger(__name__)

# 添加 markdown-it-py 导入
import markdown_it

data_conversion_bp = Blueprint('data_conversion', __name__)

ALLOWED_EXTENSIONS = {'pdf'}


def _get_upload_folder():
    try:
        from utils.config_manager import load_config, get_upload_dir
    except ImportError:
        try:
            from backend.utils.config_manager import load_config, get_upload_dir
        except ImportError:
            load_config = get_upload_dir = None
    if load_config and get_upload_dir:
        folder = get_upload_dir(load_config())
    else:
        folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


UPLOAD_FOLDER = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@data_conversion_bp.route('/md-to-html', methods=['POST'])
def markdown_to_html():
    """Markdown转HTML"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            return jsonify({'error': 'Markdown文本不能为空'}), 400

        # 使用 markdown-it-py 转换Markdown为HTML
        md = markdown_it.MarkdownIt(
            "commonmark",
            {
                "breaks": True,        # 转换 \n 为 <br>
                "html": False,         # 禁用HTML标签（防止XSS）
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)

        # 创建完整的HTML文档，包含美化样式
        full_html = build_full_html(html_content, title="Markdown转换结果", use_vars=True)

        return jsonify({
            'success': True,
            'html': full_html,  # 返回完整的HTML文档
            'original_length': len(markdown_text),
            'html_length': len(full_html)
        }), 200

    except Exception as e:
        return safe_error(e)

@data_conversion_bp.route('/preview-md', methods=['POST'])
def preview_markdown():
    """Markdown预览"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            return jsonify({'html': '<p class="empty-preview">暂无内容，请输入 Markdown 内容</p>'}), 200

        # 使用 markdown-it-py 转换Markdown为HTML用于预览
        md = markdown_it.MarkdownIt(
            "commonmark",
            {
                "breaks": True,        # 转换 \n 为 <br>
                "html": False,         # 禁用HTML标签（防止XSS）
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)

        # 创建带样式的预览HTML
        styled_html = build_preview_html(html_content)

        return jsonify({
            'success': True,
            'html': styled_html
        }), 200

    except Exception as e:
        return safe_error(e)

@data_conversion_bp.route('/preview-html', methods=['POST'])
def preview_html():
    """HTML预览"""
    try:
        data = request.get_json()
        if not data or 'html_text' not in data:
            return jsonify({'error': '请提供html_text字段'}), 400

        html_text = data['html_text']
        if not html_text.strip():
            return jsonify({'html': '<p class="empty-preview">暂无内容，请输入 HTML 内容</p>'}), 200

        return jsonify({
            'success': True,
            'html': html_text
        }), 200

    except Exception as e:
        return safe_error(e)

@data_conversion_bp.route('/html-to-md', methods=['POST'])
def html_to_markdown():
    """HTML转Markdown"""
    try:
        data = request.get_json()
        if not data or 'html_text' not in data:
            return jsonify({'error': '请提供html_text字段'}), 400

        html_text = data['html_text']
        if not html_text.strip():
            return jsonify({'error': 'HTML文本不能为空'}), 400

        # 配置html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_tables = False
        h.body_width = 0  # 不限制宽度
        h.unicode_snob = True
        h.skip_internal_links = False

        # 转换HTML为Markdown
        markdown_content = h.handle(html_text)

        # 清理多余的空白行
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)

        return jsonify({
            'success': True,
            'markdown': markdown_content.strip(),
            'original_length': len(html_text),
            'markdown_length': len(markdown_content.strip())
        }), 200

    except Exception as e:
        return safe_error(e)

@data_conversion_bp.route('/md-to-pdf', methods=['POST'])
def markdown_to_pdf():
    """Markdown转PDF - 智能选择转换器"""
    # 首先尝试使用WeasyPrint
    try:
        return markdown_to_pdf_weasyprint()
    except Exception as e:
        error_str = str(e).lower()
        # 如果WeasyPrint失败，尝试使用wkhtmltopdf
        try:
            return markdown_to_pdf_wkhtmltopdf()
        except Exception as e2:
            # 如果两种方法都失败，返回错误信息
            error_message = "PDF生成失败："

            # 检测具体的错误类型并提供针对性解决方案
            if "weasyprint" in error_str or "cairo" in error_str or "pango" in error_str:
                error_message += "检测到WeasyPrint相关错误，请检查WeasyPrint是否正确安装。"
            elif "wkhtmltopdf" in error_str or "filenotfounderror" in error_str:
                error_message += "检测到系统未安装wkhtmltopdf，请先安装wkhtmltopdf工具。"
            elif "markdown" in error_str or "html" in error_str:
                error_message += "Markdown数据处理错误，请检查输入内容格式。"
            elif "permission" in error_str or "access" in error_str:
                error_message += "文件权限错误，请检查程序是否有写入临时文件的权限。"
            elif "memory" in error_str or "out of memory" in error_str:
                error_message += "内存不足，请尝试减小输入内容的大小。"
            else:
                error_message += f"未知错误：{str(e)}"

            return jsonify({
                'error': error_message,
                'error_type': 'pdf_generation_failed'
            }), 500

def markdown_to_pdf_weasyprint():
    """Markdown转PDF - 使用WeasyPrint"""
    pdf_filename = None
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            return jsonify({'error': 'Markdown文本不能为空'}), 400

        # 使用 markdown-it-py 将Markdown转换为HTML
        md = markdown_it.MarkdownIt(
            "commonmark",
            {
                "breaks": True,        # 转换 \n 为 <br>
                "html": False,         # 禁用HTML标签（防止XSS）
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)

        # 创建完整的HTML文档，包含CSS样式
        full_html = build_full_html(html_content)

        # 创建临时PDF文件
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_filename = tmp_file.name
        tmp_file.close()  # 关闭文件句柄，让其他进程可以访问

        # 使用WeasyPrint将HTML转换为PDF
        from weasyprint import HTML, CSS
        import io
        
        # 将HTML字符串转换为PDF
        html = HTML(string=full_html)
        html.write_pdf(pdf_filename)

        # 读取PDF文件内容
        with open(pdf_filename, 'rb') as f:
            pdf_data = f.read()

        # 立即删除临时文件
        os.unlink(pdf_filename)
        pdf_filename = None

        # 返回PDF数据
        from flask import Response
        response = Response(pdf_data, mimetype='application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename='converted.pdf')
        return response

    except Exception as e:
        # 清理临时文件
        if pdf_filename and os.path.exists(pdf_filename):
            try:
                os.unlink(pdf_filename)
            except:
                pass  # 忽略删除失败的错误
        raise e  # 重新抛出异常，让调用者处理

def markdown_to_pdf_wkhtmltopdf():
    """Markdown转PDF - 使用wkhtmltopdf"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            raise ValueError('请提供markdown_text字段')

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            raise ValueError('Markdown文本不能为空')

        # 使用 markdown-it-py 将Markdown转换为HTML
        md = markdown_it.MarkdownIt(
            "commonmark",
            {
                "breaks": True,        # 转换 \n 为 <br>
                "html": False,         # 禁用HTML标签（防止XSS）
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)

        # 创建完整的HTML文档，包含CSS样式
        full_html = build_full_html(html_content)

        # 使用pdfkit将HTML转换为PDF
        import pdfkit
        import tempfile
        
        # 配置pdfkit选项
        options = {
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'margin-right': '20mm',
            'enable-local-file-access': None
        }
        
        # 生成PDF
        pdf_data = pdfkit.from_string(full_html, False, options=options)

        # 返回PDF数据
        from flask import Response
        response = Response(pdf_data, mimetype='application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename='converted.pdf')
        return response

    except FileNotFoundError as e:
        # wkhtmltopdf未安装
        raise Exception('系统中未找到wkhtmltopdf，请先安装wkhtmltopdf。请参考"wkhtmltopdf安装指南.md"进行安装。')
    except Exception as e:
        raise e  # 重新抛出异常，让调用者处理

@data_conversion_bp.route('/html-to-pdf', methods=['POST'])
def html_to_pdf():
    """HTML转PDF"""
    pdf_filename = None
    try:
        data = request.get_json()
        if not data or 'html_text' not in data:
            return jsonify({'error': '请提供html_text字段'}), 400

        html_text = data['html_text']
        if not html_text.strip():
            return jsonify({'error': 'HTML文本不能为空'}), 400

        # 创建临时PDF文件
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_filename = tmp_file.name
        tmp_file.close()  # 关闭文件句柄，让其他进程可以访问

        # 为HTML添加样式以确保PDF输出的一致性
        # 如果HTML已经包含完整的HTML结构，则直接使用
        if '<!DOCTYPE html>' in html_text and '<head>' in html_text and '<body>' in html_text:
            full_html = html_text
        else:
            # 如果是片段HTML，则包装成完整的HTML文档
            full_html = build_full_html(html_text, title="HTML转换结果")

        # 使用WeasyPrint将HTML转换为PDF
        from weasyprint import HTML
        import io
        
        # 将HTML字符串转换为PDF
        html = HTML(string=full_html)
        html.write_pdf(pdf_filename)

        # 读取PDF文件内容
        with open(pdf_filename, 'rb') as f:
            pdf_data = f.read()

        # 立即删除临时文件
        os.unlink(pdf_filename)
        pdf_filename = None

        # 返回PDF数据
        from flask import Response
        response = Response(pdf_data, mimetype='application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename='converted.pdf')
        return response

    except Exception as e:
        # 清理临时文件
        if pdf_filename and os.path.exists(pdf_filename):
            try:
                os.unlink(pdf_filename)
            except:
                pass  # 忽略删除失败的错误

        # 提供更具体的错误信息
        error_str = str(e).lower()
        error_message = "PDF生成失败："

        # 检测具体的错误类型并提供针对性解决方案
        if "weasyprint" in error_str or "cairo" in error_str or "pango" in error_str:
            error_message += "检测到WeasyPrint相关错误，请检查WeasyPrint是否正确安装。"
        elif "html" in error_str or "parse" in error_str:
            error_message += "HTML数据处理错误，请检查输入内容格式。"
        elif "permission" in error_str or "access" in error_str:
            error_message += "文件权限错误，请检查程序是否有写入临时文件的权限。"
        elif "memory" in error_str or "out of memory" in error_str:
            error_message += "内存不足，请尝试减小输入内容的大小。"
        else:
            error_message += f"未知错误：{str(e)}"

        return jsonify({
            'error': error_message,
            'error_type': 'pdf_generation_failed'
        }), 500

@data_conversion_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """上传PDF文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400

        file = request.files['file']
        if file.filename == '' or file.filename is None:
            return jsonify({'error': '没有选择文件'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(str(file.filename))
            file_path = os.path.join(_get_upload_folder(), filename)
            file.save(file_path)

            return jsonify({
                'success': True,
                'filename': filename,
                'message': '文件上传成功'
            }), 200
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

    except Exception as e:
        return safe_error(e)

@data_conversion_bp.route('/pdf-to-md', methods=['POST'])
def pdf_to_markdown():
    """PDF转Markdown"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({'error': '请提供filename字段'}), 400

        filename = data['filename']
        file_path = safe_join(_get_upload_folder(), filename)
        if file_path is None:
            return jsonify({'error': '无效的文件名'}), 403

        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404

        try:
            # 打开PDF文件
            doc = fitz.Document(file_path)  # 使用Document而不是open
            markdown_content = []
            total_pages = len(doc)

            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                text = page.get_text()

                # 添加页标题
                if total_pages > 1:
                    markdown_content.append(f'# 第{page_num + 1}页\n')

                # 处理文本，按段落分割
                paragraphs = text.split('\n\n')
                for paragraph in paragraphs:
                    paragraph = paragraph.strip()
                    if paragraph:
                        # 简单的标题检测（基于字体大小或位置，这里简化处理）
                        if len(paragraph) < 100 and not paragraph.endswith('.'):
                            markdown_content.append(f'## {paragraph}\n')
                        else:
                            markdown_content.append(f'{paragraph}\n\n')

            doc.close()

            # 合并所有内容
            final_markdown = ''.join(markdown_content)

            # 清理文件
            os.unlink(file_path)

            return jsonify({
                'success': True,
                'markdown': final_markdown,
                'pages': total_pages,
                'characters': len(final_markdown)
            }), 200

        except Exception as e:
            # 清理文件
            if os.path.exists(file_path):
                os.unlink(file_path)
            return jsonify({'error': f'PDF处理错误: {str(e)}'}), 500

    except Exception as e:
        return safe_error(e)
