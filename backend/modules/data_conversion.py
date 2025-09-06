from flask import Blueprint, request, jsonify, send_file
import html2text
import os
import tempfile
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF for PDF processing
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from bs4 import BeautifulSoup
import re

# 添加 markdown-it-py 导入
import markdown_it

data_conversion_bp = Blueprint('data_conversion', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
                "html": True,          # 启用HTML标签
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)

        # 创建完整的HTML文档，包含美化样式
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown转换结果</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --background-color: #ffffff;
            --text-color: #334155;
            --border-color: #e2e8f0;
            --code-background: #f8fafc;
            --blockquote-background: #f1f5f9;
            --table-header: #f1f5f9;
            --table-row-even: #f8fafc;
            --link-color: #2563eb;
            --link-hover: #1d4ed8;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: var(--text-color);
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background-color: var(--background-color);
            tab-size: 4;
        }}

        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }}

        h1 {{
            font-size: 2.5em;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}

        h2 {{
            font-size: 2em;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 12px;
            margin-top: 40px;
        }}

        h3 {{
            font-size: 1.75em;
            color: #1e293b;
            margin-top: 35px;
        }}

        h4 {{
            font-size: 1.5em;
            color: #334155;
            margin-top: 30px;
        }}

        h5 {{
            font-size: 1.25em;
            color: #475569;
            margin-top: 25px;
        }}

        h6 {{
            font-size: 1.1em;
            color: #64748b;
            margin-top: 20px;
        }}

        /* 段落样式 */
        p {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.05em;
            text-align: justify;
        }}

        /* 链接样式 */
        a {{
            color: var(--link-color);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s ease;
        }}

        a:hover {{
            color: var(--link-hover);
            border-bottom: 1px solid var(--link-hover);
        }}

        /* 代码样式 */
        code {{
            padding: 0.3em 0.5em;
            margin: 0 0.2em;
            font-size: 0.9em;
            background-color: var(--code-background);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }}

        pre {{
            padding: 20px;
            overflow: auto;
            font-size: 0.95em;
            line-height: 1.5;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 25px 0;
            border: 1px solid var(--border-color);
        }}

        pre code {{
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }}

        /* 引用块样式 */
        blockquote {{
            padding: 20px 25px;
            margin: 25px 0;
            color: #475569;
            border-left: 5px solid var(--primary-color);
            background-color: var(--blockquote-background);
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        blockquote p {{
            margin: 0;
            font-style: italic;
        }}

        blockquote::before {{
            content: "\\201C";
            font-size: 3em;
            color: var(--primary-color);
            opacity: 0.3;
            line-height: 0.1em;
            margin-right: 0.25em;
            vertical-align: -0.4em;
        }}

        /* 列表样式 */
        ul, ol {{
            padding-left: 2.5em;
            margin: 20px 0;
        }}

        li {{
            margin-bottom: 10px;
            line-height: 1.7;
        }}

        ul li {{
            list-style-type: disc;
        }}

        ul ul li {{
            list-style-type: circle;
        }}

        ul ul ul li {{
            list-style-type: square;
        }}

        ol li {{
            list-style-type: decimal;
        }}

        /* 嵌套列表处理 */
        ul ul, ul ol, ol ul, ol ol {{
            margin-top: 10px;
            margin-bottom: 10px;
        }}

        li > p {{
            margin-top: 0;
            margin-bottom: 0;
        }}

        /* 特别处理列表项中的换行 */
        li br {{
            display: inline;
        }}

        /* 表格样式 */
        table {{
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}

        table th, table td {{
            padding: 12px 15px;
            border: 1px solid var(--border-color);
        }}

        table th {{
            background-color: var(--table-header);
            font-weight: 600;
            text-align: left;
            color: #1e293b;
        }}

        table tr:nth-child(2n) {{
            background-color: var(--table-row-even);
        }}

        table tr:hover {{
            background-color: #e0f2fe;
        }}

        /* 分隔线样式 */
        hr {{
            height: 2px;
            padding: 0;
            margin: 40px 0;
            background: linear-gradient(to right, transparent, var(--primary-color), transparent);
            border: 0;
        }}

        /* 图片样式 */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }}

        /* 内联代码高亮 */
        p code {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-weight: 500;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            body {{
                padding: 20px;
                font-size: 0.95em;
            }}

            h1 {{
                font-size: 2em;
            }}

            h2 {{
                font-size: 1.7em;
            }}

            h3 {{
                font-size: 1.5em;
            }}

            pre {{
                padding: 15px;
                font-size: 0.85em;
            }}
        }}

        /* 打印样式 */
        @media print {{
            body {{
                padding: 20px;
                max-width: 100%;
            }}

            pre {{
                box-shadow: none;
                border: 1px solid #ccc;
            }}

            blockquote {{
                box-shadow: none;
                border: 1px solid #ccc;
            }}

            table {{
                box-shadow: none;
                border: 1px solid #ccc;
            }}
        }}
    </style>
</head>
<body>
    <article>
        {html_content}
    </article>
</body>
</html>"""

        return jsonify({
            'success': True,
            'html': full_html,  # 返回完整的HTML文档
            'original_length': len(markdown_text),
            'html_length': len(full_html)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
                "html": True,          # 启用HTML标签
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)

        # 创建带样式的预览HTML
        styled_html = f"""<div class="markdown-preview">
    <style>
        .markdown-preview {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: #334155;
            max-width: 100%;
            padding: 20px;
            background-color: #ffffff;
        }}

        .markdown-preview h1,
        .markdown-preview h2,
        .markdown-preview h3,
        .markdown-preview h4,
        .markdown-preview h5,
        .markdown-preview h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }}

        .markdown-preview h1 {{
            font-size: 2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.3em;
        }}

        .markdown-preview h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.3em;
        }}

        .markdown-preview h3 {{
            font-size: 1.25em;
        }}

        .markdown-preview p {{
            margin-top: 0;
            margin-bottom: 16px;
            text-align: justify;
        }}

        .markdown-preview a {{
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s ease;
        }}

        .markdown-preview a:hover {{
            color: #1d4ed8;
            border-bottom: 1px solid #1d4ed8;
        }}

        .markdown-preview code {{
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }}

        .markdown-preview pre {{
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 8px;
            tab-size: 4;
            white-space: pre-wrap;
            margin-bottom: 16px;
            border: 1px solid #e2e8f0;
        }}

        .markdown-preview pre code {{
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }}

        .markdown-preview blockquote {{
            padding: 0 1em;
            color: #64748b;
            border-left: 0.25em solid #2563eb;
            background-color: #f1f5f9;
            border-radius: 0 4px 4px 0;
            margin: 16px 0;
        }}

        .markdown-preview ul,
        .markdown-preview ol {{
            padding-left: 2em;
            margin-top: 0;
            margin-bottom: 16px;
        }}

        .markdown-preview li {{
            margin-bottom: 0.25em;
            line-height: 1.5;
        }}

        .markdown-preview ul ul,
        .markdown-preview ul ol,
        .markdown-preview ol ul,
        .markdown-preview ol ol {{
            margin-top: 0;
            margin-bottom: 0;
        }}

        .markdown-preview li > p {{
            margin-top: 0;
            margin-bottom: 0;
        }}

        .markdown-preview table {{
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 16px 0;
        }}

        .markdown-preview table th,
        .markdown-preview table td {{
            padding: 6px 13px;
            border: 1px solid #e2e8f0;
        }}

        .markdown-preview table th {{
            background-color: #f1f5f9;
            font-weight: 600;
        }}

        .markdown-preview table tr:nth-child(2n) {{
            background-color: #f8fafc;
        }}

        .markdown-preview hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e2e8f0;
            border: 0;
        }}

        .markdown-preview img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
    </style>
    {html_content}
</div>"""

        return jsonify({
            'success': True,
            'html': styled_html
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500

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
        return jsonify({'error': str(e)}), 500

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
                "html": True,          # 启用HTML标签
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)
        
        # 创建完整的HTML文档，包含CSS样式
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown转换结果</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: #334155;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background-color: #ffffff;
            tab-size: 4;
        }}

        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }}

        h1 {{
            font-size: 2.5em;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}

        h2 {{
            font-size: 2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 12px;
            margin-top: 40px;
        }}

        h3 {{
            font-size: 1.75em;
            color: #1e293b;
            margin-top: 35px;
        }}

        h4 {{
            font-size: 1.5em;
            color: #334155;
            margin-top: 30px;
        }}

        h5 {{
            font-size: 1.25em;
            color: #475569;
            margin-top: 25px;
        }}

        h6 {{
            font-size: 1.1em;
            color: #64748b;
            margin-top: 20px;
        }}

        /* 段落样式 */
        p {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.05em;
            text-align: justify;
        }}

        /* 链接样式 */
        a {{
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
        }}

        a:hover {{
            color: #1d4ed8;
            border-bottom: 1px solid #1d4ed8;
        }}

        /* 代码样式 */
        code {{
            padding: 0.3em 0.5em;
            margin: 0 0.2em;
            font-size: 0.9em;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }}

        pre {{
            padding: 20px;
            overflow: auto;
            font-size: 0.95em;
            line-height: 1.5;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 25px 0;
            border: 1px solid #e2e8f0;
        }}

        pre code {{
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }}

        /* 引用块样式 */
        blockquote {{
            padding: 20px 25px;
            margin: 25px 0;
            color: #475569;
            border-left: 5px solid #2563eb;
            background-color: #f1f5f9;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        blockquote p {{
            margin: 0;
            font-style: italic;
        }}

        blockquote::before {{
            content: "\\201C";
            font-size: 3em;
            color: #2563eb;
            opacity: 0.3;
            line-height: 0.1em;
            margin-right: 0.25em;
            vertical-align: -0.4em;
        }}

        /* 列表样式 */
        ul, ol {{
            padding-left: 2.5em;
            margin: 20px 0;
        }}

        li {{
            margin-bottom: 10px;
            line-height: 1.7;
        }}

        ul li {{
            list-style-type: disc;
        }}

        ul ul li {{
            list-style-type: circle;
        }}

        ul ul ul li {{
            list-style-type: square;
        }}

        ol li {{
            list-style-type: decimal;
        }}

        /* 嵌套列表处理 */
        ul ul, ul ol, ol ul, ol ol {{
            margin-top: 10px;
            margin-bottom: 10px;
        }}

        li > p {{
            margin-top: 0;
            margin-bottom: 0;
        }}

        /* 表格样式 */
        table {{
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}

        table th, table td {{
            padding: 12px 15px;
            border: 1px solid #e2e8f0;
        }}

        table th {{
            background-color: #f1f5f9;
            font-weight: 600;
            text-align: left;
            color: #1e293b;
        }}

        table tr:nth-child(2n) {{
            background-color: #f8fafc;
        }}

        table tr:hover {{
            background-color: #e0f2fe;
        }}

        /* 分隔线样式 */
        hr {{
            height: 2px;
            padding: 0;
            margin: 40px 0;
            background: linear-gradient(to right, transparent, #2563eb, transparent);
            border: 0;
        }}

        /* 图片样式 */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }}

        /* 内联代码高亮 */
        p code {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <article>
        {html_content}
    </article>
</body>
</html>"""

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
                "html": True,          # 启用HTML标签
                "linkify": True,       # 自动转换URL为链接
                "typographer": True,   # 启用智能引号等排版替换
            }
        ).enable(['table', 'strikethrough', 'code', 'fence', 'emphasis', 'list'])

        html_content = md.render(markdown_text)
        
        # 创建完整的HTML文档，包含CSS样式
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown转换结果</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: #334155;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background-color: #ffffff;
            tab-size: 4;
        }}

        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }}

        h1 {{
            font-size: 2.5em;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}

        h2 {{
            font-size: 2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 12px;
            margin-top: 40px;
        }}

        h3 {{
            font-size: 1.75em;
            color: #1e293b;
            margin-top: 35px;
        }}

        h4 {{
            font-size: 1.5em;
            color: #334155;
            margin-top: 30px;
        }}

        h5 {{
            font-size: 1.25em;
            color: #475569;
            margin-top: 25px;
        }}

        h6 {{
            font-size: 1.1em;
            color: #64748b;
            margin-top: 20px;
        }}

        /* 段落样式 */
        p {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.05em;
            text-align: justify;
        }}

        /* 链接样式 */
        a {{
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
        }}

        a:hover {{
            color: #1d4ed8;
            border-bottom: 1px solid #1d4ed8;
        }}

        /* 代码样式 */
        code {{
            padding: 0.3em 0.5em;
            margin: 0 0.2em;
            font-size: 0.9em;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }}

        pre {{
            padding: 20px;
            overflow: auto;
            font-size: 0.95em;
            line-height: 1.5;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 25px 0;
            border: 1px solid #e2e8f0;
        }}

        pre code {{
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }}

        /* 引用块样式 */
        blockquote {{
            padding: 20px 25px;
            margin: 25px 0;
            color: #475569;
            border-left: 5px solid #2563eb;
            background-color: #f1f5f9;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        blockquote p {{
            margin: 0;
            font-style: italic;
        }}

        blockquote::before {{
            content: "\\201C";
            font-size: 3em;
            color: #2563eb;
            opacity: 0.3;
            line-height: 0.1em;
            margin-right: 0.25em;
            vertical-align: -0.4em;
        }}

        /* 列表样式 */
        ul, ol {{
            padding-left: 2.5em;
            margin: 20px 0;
        }}

        li {{
            margin-bottom: 10px;
            line-height: 1.7;
        }}

        ul li {{
            list-style-type: disc;
        }}

        ul ul li {{
            list-style-type: circle;
        }}

        ul ul ul li {{
            list-style-type: square;
        }}

        ol li {{
            list-style-type: decimal;
        }}

        /* 嵌套列表处理 */
        ul ul, ul ol, ol ul, ol ol {{
            margin-top: 10px;
            margin-bottom: 10px;
        }}

        li > p {{
            margin-top: 0;
            margin-bottom: 0;
        }}

        /* 表格样式 */
        table {{
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}

        table th, table td {{
            padding: 12px 15px;
            border: 1px solid #e2e8f0;
        }}

        table th {{
            background-color: #f1f5f9;
            font-weight: 600;
            text-align: left;
            color: #1e293b;
        }}

        table tr:nth-child(2n) {{
            background-color: #f8fafc;
        }}

        table tr:hover {{
            background-color: #e0f2fe;
        }}

        /* 分隔线样式 */
        hr {{
            height: 2px;
            padding: 0;
            margin: 40px 0;
            background: linear-gradient(to right, transparent, #2563eb, transparent);
            border: 0;
        }}

        /* 图片样式 */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }}

        /* 内联代码高亮 */
        p code {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <article>
        {html_content}
    </article>
</body>
</html>"""

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
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML转换结果</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: #334155;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background-color: #ffffff;
            tab-size: 4;
        }}

        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }}

        h1 {{
            font-size: 2.5em;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}

        h2 {{
            font-size: 2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 12px;
            margin-top: 40px;
        }}

        h3 {{
            font-size: 1.75em;
            color: #1e293b;
            margin-top: 35px;
        }}

        h4 {{
            font-size: 1.5em;
            color: #334155;
            margin-top: 30px;
        }}

        h5 {{
            font-size: 1.25em;
            color: #475569;
            margin-top: 25px;
        }}

        h6 {{
            font-size: 1.1em;
            color: #64748b;
            margin-top: 20px;
        }}

        /* 段落样式 */
        p {{
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.05em;
            text-align: justify;
        }}

        /* 链接样式 */
        a {{
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
        }}

        a:hover {{
            color: #1d4ed8;
            border-bottom: 1px solid #1d4ed8;
        }}

        /* 代码样式 */
        code {{
            padding: 0.3em 0.5em;
            margin: 0 0.2em;
            font-size: 0.9em;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }}

        pre {{
            padding: 20px;
            overflow: auto;
            font-size: 0.95em;
            line-height: 1.5;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 25px 0;
            border: 1px solid #e2e8f0;
        }}

        pre code {{
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }}

        /* 引用块样式 */
        blockquote {{
            padding: 20px 25px;
            margin: 25px 0;
            color: #475569;
            border-left: 5px solid #2563eb;
            background-color: #f1f5f9;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        blockquote p {{
            margin: 0;
            font-style: italic;
        }}

        blockquote::before {{
            content: "\\201C";
            font-size: 3em;
            color: #2563eb;
            opacity: 0.3;
            line-height: 0.1em;
            margin-right: 0.25em;
            vertical-align: -0.4em;
        }}

        /* 列表样式 */
        ul, ol {{
            padding-left: 2.5em;
            margin: 20px 0;
        }}

        li {{
            margin-bottom: 10px;
            line-height: 1.7;
        }}

        ul li {{
            list-style-type: disc;
        }}

        ul ul li {{
            list-style-type: circle;
        }}

        ul ul ul li {{
            list-style-type: square;
        }}

        ol li {{
            list-style-type: decimal;
        }}

        /* 嵌套列表处理 */
        ul ul, ul ol, ol ul, ol ol {{
            margin-top: 10px;
            margin-bottom: 10px;
        }}

        li > p {{
            margin-top: 0;
            margin-bottom: 0;
        }}

        /* 表格样式 */
        table {{
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}

        table th, table td {{
            padding: 12px 15px;
            border: 1px solid #e2e8f0;
        }}

        table th {{
            background-color: #f1f5f9;
            font-weight: 600;
            text-align: left;
            color: #1e293b;
        }}

        table tr:nth-child(2n) {{
            background-color: #f8fafc;
        }}

        table tr:hover {{
            background-color: #e0f2fe;
        }}

        /* 分隔线样式 */
        hr {{
            height: 2px;
            padding: 0;
            margin: 40px 0;
            background: linear-gradient(to right, transparent, #2563eb, transparent);
            border: 0;
        }}

        /* 图片样式 */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }}

        /* 内联代码高亮 */
        p code {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <article>
        {html_text}
    </article>
</body>
</html>"""

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
            filename = secure_filename(str(file.filename))  # 确保filename是字符串类型
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            return jsonify({
                'success': True,
                'filename': filename,
                'message': '文件上传成功'
            }), 200
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_conversion_bp.route('/pdf-to-md', methods=['POST'])
def pdf_to_markdown():
    """PDF转Markdown"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({'error': '请提供filename字段'}), 400

        filename = data['filename']
        file_path = os.path.join(UPLOAD_FOLDER, filename)

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
        return jsonify({'error': str(e)}), 500
