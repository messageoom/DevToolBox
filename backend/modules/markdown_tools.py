from flask import Blueprint, request, jsonify
import markdown
import html
from bs4 import BeautifulSoup
import re

markdown_tools_bp = Blueprint('markdown_tools', __name__)

@markdown_tools_bp.route('/to-html', methods=['POST'])
def markdown_to_html():
    """Markdown转HTML"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            return jsonify({'error': 'Markdown文本不能为空'}), 400

        # 转换Markdown为HTML
        html_content = markdown.markdown(
            markdown_text,
            extensions=[
                'extra',           # 包含表格、代码块等扩展
                'codehilite',      # 代码高亮
                'toc',            # 目录
                'fenced_code',     # 围栏代码块
                'tables',          # 表格支持
                'nl2br'            # 换行转<br>
            ]
        )

        return jsonify({
            'success': True,
            'html': html_content,
            'original_length': len(markdown_text),
            'html_length': len(html_content)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/to-plain', methods=['POST'])
def markdown_to_plain():
    """Markdown转纯文本"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            return jsonify({'error': 'Markdown文本不能为空'}), 400

        # 转换Markdown为HTML，然后提取纯文本
        html_content = markdown.markdown(markdown_text)
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取纯文本
        plain_text = soup.get_text()

        # 清理多余的空白字符
        plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text.strip())

        return jsonify({
            'success': True,
            'plain_text': plain_text,
            'original_length': len(markdown_text),
            'plain_length': len(plain_text)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/escape', methods=['POST'])
def escape_markdown():
    """转义Markdown特殊字符"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供text字段'}), 400

        text = data['text']

        # Markdown特殊字符转义
        escaped_text = re.sub(r'([\\`*_{}[\]()#+\-.!])', r'\\\1', text)

        return jsonify({
            'success': True,
            'escaped': escaped_text,
            'original_length': len(text),
            'escaped_length': len(escaped_text)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/unescape', methods=['POST'])
def unescape_markdown():
    """反转义Markdown特殊字符"""
    try:
        data = request.get_json()
        if not data or 'escaped_text' not in data:
            return jsonify({'error': '请提供escaped_text字段'}), 400

        escaped_text = data['escaped_text']

        # 反转义Markdown特殊字符
        unescaped_text = re.sub(r'\\([\\`*_{}[\]()#+\-.!])', r'\1', escaped_text)

        return jsonify({
            'success': True,
            'unescaped': unescaped_text,
            'original_length': len(escaped_text),
            'unescaped_length': len(unescaped_text)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/extract-links', methods=['POST'])
def extract_markdown_links():
    """提取Markdown中的链接"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']

        # 正则表达式匹配Markdown链接
        # [text](url) 格式
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, markdown_text)

        # 提取链接信息
        extracted_links = []
        for text, url in links:
            extracted_links.append({
                'text': text,
                'url': url,
                'full_match': f'[{text}]({url})'
            })

        return jsonify({
            'success': True,
            'links': extracted_links,
            'total_links': len(extracted_links),
            'original_length': len(markdown_text)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/extract-images', methods=['POST'])
def extract_markdown_images():
    """提取Markdown中的图片"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']

        # 正则表达式匹配Markdown图片
        # ![alt](url) 或 ![alt](url "title") 格式
        image_pattern = r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)'
        images = re.findall(image_pattern, markdown_text)

        # 提取图片信息
        extracted_images = []
        for alt, url, title in images:
            extracted_images.append({
                'alt': alt,
                'url': url,
                'title': title or '',
                'full_match': f'![{alt}]({url})' + (f' "{title}"' if title else '')
            })

        return jsonify({
            'success': True,
            'images': extracted_images,
            'total_images': len(extracted_images),
            'original_length': len(markdown_text)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/table-to-markdown', methods=['POST'])
def table_to_markdown():
    """HTML表格转Markdown表格"""
    try:
        data = request.get_json()
        if not data or 'html_table' not in data:
            return jsonify({'error': '请提供html_table字段'}), 400

        html_table = data['html_table']

        try:
            soup = BeautifulSoup(html_table, 'html.parser')
            table = soup.find('table')

            if not table:
                return jsonify({'error': '未找到有效的HTML表格'}), 400

            # 提取表格数据
            rows = []
            headers = []

            # 处理表头
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [cell.get_text(strip=True) for cell in header_row.find_all(['th', 'td'])]

            # 处理表体
            tbody = table.find('tbody')
            if tbody:
                for tr in tbody.find_all('tr'):
                    row_data = [cell.get_text(strip=True) for cell in tr.find_all(['td', 'th'])]
                    if row_data:
                        rows.append(row_data)

            # 如果没有表头，从第一行数据中提取
            if not headers and rows:
                headers = rows.pop(0)

            # 生成Markdown表格
            if not headers:
                return jsonify({'error': '无法提取表格头部'}), 400

            markdown_table = []

            # 添加表头
            markdown_table.append('| ' + ' | '.join(headers) + ' |')
            markdown_table.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')

            # 添加数据行
            for row in rows:
                # 确保行数据长度与表头一致
                while len(row) < len(headers):
                    row.append('')
                row = row[:len(headers)]
                markdown_table.append('| ' + ' | '.join(row) + ' |')

            markdown_result = '\n'.join(markdown_table)

            return jsonify({
                'success': True,
                'markdown_table': markdown_result,
                'headers': headers,
                'rows_count': len(rows),
                'columns_count': len(headers)
            }), 200

        except Exception as e:
            return jsonify({'error': f'HTML解析错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/validate', methods=['POST'])
def validate_markdown():
    """验证Markdown语法"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']

        try:
            # 尝试转换Markdown为HTML来验证语法
            html_content = markdown.markdown(markdown_text)

            # 基本语法检查
            issues = []

            # 检查未闭合的链接
            open_links = len(re.findall(r'\[([^\]]*)$', markdown_text, re.MULTILINE))
            if open_links > 0:
                issues.append(f'发现 {open_links} 个未闭合的链接')

            # 检查未闭合的图片
            open_images = len(re.findall(r'!\[([^\]]*)$', markdown_text, re.MULTILINE))
            if open_images > 0:
                issues.append(f'发现 {open_images} 个未闭合的图片')

            # 检查未闭合的代码块
            code_blocks = len(re.findall(r'```', markdown_text))
            if code_blocks % 2 != 0:
                issues.append('代码块没有正确闭合')

            # 检查未闭合的行内代码
            inline_codes = len(re.findall(r'`', markdown_text))
            if inline_codes % 2 != 0:
                issues.append('行内代码没有正确闭合')

            return jsonify({
                'success': True,
                'valid': len(issues) == 0,
                'issues': issues,
                'issues_count': len(issues),
                'original_length': len(markdown_text)
            }), 200

        except Exception as e:
            return jsonify({
                'success': True,
                'valid': False,
                'issues': [f'Markdown语法错误: {str(e)}'],
                'issues_count': 1,
                'original_length': len(markdown_text)
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@markdown_tools_bp.route('/stats', methods=['POST'])
def markdown_stats():
    """Markdown文档统计"""
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']

        # 统计信息
        stats = {
            'characters': len(markdown_text),
            'characters_no_spaces': len(markdown_text.replace(' ', '').replace('\n', '').replace('\t', '')),
            'words': len(markdown_text.split()),
            'lines': len(markdown_text.splitlines()),
            'paragraphs': len([p for p in markdown_text.split('\n\n') if p.strip()]),
            'headings': {
                'h1': len(re.findall(r'^#\s', markdown_text, re.MULTILINE)),
                'h2': len(re.findall(r'^##\s', markdown_text, re.MULTILINE)),
                'h3': len(re.findall(r'^###\s', markdown_text, re.MULTILINE)),
                'h4': len(re.findall(r'^####\s', markdown_text, re.MULTILINE)),
                'h5': len(re.findall(r'^#####\s', markdown_text, re.MULTILINE)),
                'h6': len(re.findall(r'^######\s', markdown_text, re.MULTILINE))
            },
            'links': len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_text)),
            'images': len(re.findall(r'!\[([^\]]*)\]\(([^)\s]+)', markdown_text)),
            'code_blocks': len(re.findall(r'```', markdown_text)) // 2,
            'inline_codes': len(re.findall(r'`[^`]+`', markdown_text)),
            'lists': {
                'unordered': len(re.findall(r'^[\s]*[-\*\+]\s', markdown_text, re.MULTILINE)),
                'ordered': len(re.findall(r'^[\s]*\d+\.\s', markdown_text, re.MULTILINE))
            },
            'tables': len(re.findall(r'\|.*\|.*\|', markdown_text)),
            'blockquotes': len(re.findall(r'^>\s', markdown_text, re.MULTILINE))
        }

        # 计算标题总数
        stats['headings']['total'] = sum(stats['headings'].values())

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
