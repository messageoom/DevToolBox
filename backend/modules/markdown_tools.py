from flask import Blueprint, request, jsonify
import markdown
from markdown_it import MarkdownIt
import html
from bs4 import BeautifulSoup
import re

markdown_tools_bp = Blueprint('markdown_tools', __name__)

@markdown_tools_bp.route('/to-html', methods=['POST'])
def markdown_to_html():
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            return jsonify({'error': 'Markdown文本不能为空'}), 400

        # 使用 markdown-it-py 解析 Markdown，嵌套列表100%兼容
        md = MarkdownIt()
        html_content = md.render(markdown_text)

        # 创建完整的HTML文档，包含样式

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    code_themes_css = """
    /* 代码主题样式 */
    .code-github pre {
        background-color: #f6f8fa !important;
        color: #24292e !important;
        border: 1px solid #e1e4e8 !important;
        border-radius: 6px !important;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
        padding: 16px !important;
        overflow: auto !important;
    }

    .code-monokai pre {
        background-color: #272822 !important;
        color: #f8f8f2 !important;
        border: 1px solid #49483e !important;
        border-radius: 6px !important;
        font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
        padding: 16px !important;
        overflow: auto !important;
    }

    .code-dracula pre {
        background-color: #282a36 !important;
        color: #f8f8f2 !important;
        border: 1px solid #44475a !important;
        border-radius: 6px !important;
        font-family: "Fira Code", "Monaco", "Menlo", monospace !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
        padding: 16px !important;
        overflow: auto !important;
    }

    .code-solarized pre {
        background-color: #fdf6e3 !important;
        color: #586e75 !important;
        border: 1px solid #eee8d5 !important;
        border-radius: 6px !important;
        font-family: "Source Code Pro", "Monaco", monospace !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
        padding: 16px !important;
        overflow: auto !important;
    }

    .code-atom pre {
        background-color: #fafafa !important;
        color: #383a42 !important;
        border: 1px solid #e5e5e6 !important;
        border-radius: 6px !important;
        font-family: "Fira Code", "Monaco", monospace !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
        padding: 16px !important;
        overflow: auto !important;
    }

    .code-vs-code pre {
        background-color: #1e1e1e !important;
        color: #d4d4d4 !important;
        border: 1px solid #3e3e42 !important;
        border-radius: 6px !important;
        font-family: "Consolas", "Monaco", monospace !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
        padding: 16px !important;
        overflow: auto !important;
    }
    """

    css_styles = """
    /* 全局兜底列表缩进，防止样式被覆盖 */
    ul, ol { padding-left: 2em !important; }
    /* 基础样式重置 */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    html {
        height: 100%;
        font-size: 16px;
    }

    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #fff;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        overflow-x: hidden;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* 重置默认样式 */
    h1, h2, h3, h4, h5, h6 {
        font-weight: normal;
        font-size: inherit;
    }

    p {
        margin: 0;
    }

    a {
        color: inherit;
        text-decoration: none;
    }

    img {
        max-width: 100%;
        height: auto;
    }

    table {
        border-collapse: collapse;
        border-spacing: 0;
    }

    pre, code {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    }

    /* Markdown 内容容器 - 与前端预览组件完全匹配 */
    .preview-content {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: #333;
        word-wrap: break-word;
        overflow-wrap: break-word;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* 确保内容区域正确显示 */
    .preview-content * {
        max-width: 100%;
    }

    /* 标题样式 - 完全匹配前端 :deep() 选择器 */
    .preview-content h1,
    .preview-content h2,
    .preview-content h3,
    .preview-content h4,
    .preview-content h5,
    .preview-content h6 {
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        color: #333;
    }

    .preview-content h1 {
        font-size: 2em;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.3em;
    }

    .preview-content h2 {
        font-size: 1.5em;
        border-bottom: 1px solid #eee;
        padding-bottom: 0.3em;
    }

    .preview-content h3 {
        font-size: 1.2em;
    }

    .preview-content h4 {
        font-size: 1.1em;
    }

    .preview-content h5 {
        font-size: 1.0em;
    }

    .preview-content h6 {
        font-size: 0.9em;
    }

    /* 段落样式 */
    .preview-content p {
        margin: 1em 0;
    }

    /* 链接样式 */
    .preview-content a {
        color: #409eff;
        text-decoration: none;
    }

    .preview-content a:hover {
        text-decoration: underline;
    }

    /* 列表样式 - 恢复默认列表样式 */
    .preview-content ul {
        list-style-type: disc;
        margin: 1em 0;
        padding-left: 2em;
    }

    .preview-content ol {
        list-style-type: decimal;
        margin: 1em 0;
        padding-left: 2em;
    }

    .preview-content li {
        margin: 0.5em 0;
        display: list-item;
    }

    /* 嵌套列表样式 */
    .preview-content ul ul {
        list-style-type: circle;
    }

    .preview-content ul ul ul {
        list-style-type: square;
    }

    .preview-content ol ol {
        list-style-type: lower-alpha;
    }

    .preview-content ol ol ol {
        list-style-type: lower-roman;
    }

    .preview-content ul ul,
    .preview-content ol ol,
    .preview-content ul ol,
    .preview-content ol ul {
        margin: 0.5em 0;
        padding-left: 1.5em;
    }

    /* 代码样式 */
    .preview-content code {
        background-color: #f6f8fa;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 0.9em;
    }

    /* 代码块样式 */
    .preview-content pre {
        background-color: #f6f8fa;
        padding: 16px;
        border-radius: 6px;
        overflow-x: auto;
        margin: 1em 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    .preview-content pre code {
        background-color: transparent;
        padding: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* 表格样式 */
    .preview-content table {
        border-collapse: collapse;
        width: 100%;
        margin: 1em 0;
    }

    .preview-content th,
    .preview-content td {
        border: 1px solid #ddd;
        padding: 8px 12px;
        text-align: left;
    }

    .preview-content th {
        background-color: #f8f9fa;
        font-weight: bold;
    }

    /* 引用块样式 */
    .preview-content blockquote {
        border-left: 4px solid #ddd;
        padding-left: 16px;
        margin: 1em 0;
        color: #666;
    }

    /* 水平线样式 */
    .preview-content hr {
        border: none;
        height: 1px;
        background-color: #eee;
        margin: 2em 0;
    }

    /* 图片样式 */
    .preview-content img {
        max-width: 100%;
        height: auto;
        border-radius: 4px;
    }

    /* 强调样式 */
    .preview-content strong,
    .preview-content b {
        font-weight: bold;
    }

    .preview-content em,
    .preview-content i {
        font-style: italic;
    }

    /* 任务列表样式 */
    .preview-content input[type="checkbox"] {
        margin-right: 0.5em;
    }

    /* 语法高亮样式 (针对 codehilite 扩展) */
    .codehilite .hll { background-color: #ffffcc }
    .codehilite .c { color: #408080; font-style: italic } /* Comment */
    .codehilite .err { border: 1px solid #FF0000 } /* Error */
    .codehilite .k { color: #008000; font-weight: bold } /* Keyword */
    .codehilite .o { color: #666666 } /* Operator */
    .codehilite .ch { color: #408080; font-style: italic } /* Comment.Hashbang */
    .codehilite .cm { color: #408080; font-style: italic } /* Comment.Multiline */
    .codehilite .cp { color: #BC7A00 } /* Comment.Preproc */
    .codehilite .cpf { color: #408080; font-style: italic } /* Comment.PreprocFile */
    .codehilite .c1 { color: #408080; font-style: italic } /* Comment.Single */
    .codehilite .cs { color: #408080; font-style: italic } /* Comment.Special */
    .codehilite .gd { color: #A00000 } /* Generic.Deleted */
    .codehilite .ge { font-style: italic } /* Generic.Emph */
    .codehilite .gr { color: #FF0000 } /* Generic.Error */
    .codehilite .gh { color: #000080; font-weight: bold } /* Generic.Heading */
    .codehilite .gi { color: #00A000 } /* Generic.Inserted */
    .codehilite .go { color: #888888 } /* Generic.Output */
    .codehilite .gp { color: #000080; font-weight: bold } /* Generic.Prompt */
    .codehilite .gs { font-weight: bold } /* Generic.Strong */
    .codehilite .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
    .codehilite .gt { color: #0044DD } /* Generic.Traceback */
    .codehilite .kc { color: #008000; font-weight: bold } /* Keyword.Constant */
    .codehilite .kd { color: #008000; font-weight: bold } /* Keyword.Declaration */
    .codehilite .kn { color: #008000; font-weight: bold } /* Keyword.Namespace */
    .codehilite .kp { color: #008000 } /* Keyword.Pseudo */
    .codehilite .kr { color: #008000; font-weight: bold } /* Keyword.Reserved */
    .codehilite .kt { color: #B00040 } /* Keyword.Type */
    .codehilite .m { color: #666666 } /* Literal.Number */
    .codehilite .s { color: #BA2121 } /* Literal.String */
    .codehilite .na { color: #7D9029 } /* Name.Attribute */
    .codehilite .nb { color: #008000 } /* Name.Builtin */
    .codehilite .nc { color: #0000FF; font-weight: bold } /* Name.Class */
    .codehilite .no { color: #880000 } /* Name.Constant */
    .codehilite .nd { color: #AA22FF } /* Name.Decorator */
    .codehilite .ni { color: #999999; font-weight: bold } /* Name.Entity */
    .codehilite .ne { color: #D2413A; font-weight: bold } /* Name.Exception */
    .codehilite .nf { color: #0000FF } /* Name.Function */
    .codehilite .nl { color: #A0A000 } /* Name.Label */
    .codehilite .nn { color: #0000FF; font-weight: bold } /* Name.Namespace */
    .codehilite .nt { color: #008000; font-weight: bold } /* Name.Tag */
    .codehilite .nv { color: #19177C } /* Name.Variable */
    .codehilite .ow { color: #AA22FF; font-weight: bold } /* Operator.Word */
    .codehilite .w { color: #bbbbbb } /* Text.Whitespace */
    .codehilite .mb { color: #666666 } /* Literal.Number.Bin */
    .codehilite .mf { color: #666666 } /* Literal.Number.Float */
    .codehilite .mh { color: #666666 } /* Literal.Number.Hex */
    .codehilite .mi { color: #666666 } /* Literal.Number.Integer */
    .codehilite .mo { color: #666666 } /* Literal.Number.Oct */
    .codehilite .sa { color: #BA2121 } /* Literal.String.Affix */
    .codehilite .sb { color: #BA2121 } /* Literal.String.Backtick */
    .codehilite .sc { color: #BA2121 } /* Literal.String.Char */
    .codehilite .dl { color: #BA2121 } /* Literal.String.Delimiter */
    .codehilite .sd { color: #BA2121 } /* Literal.String.Doc */
    .codehilite .s2 { color: #BA2121 } /* Literal.String.Double */
    .codehilite .se { color: #BA2121 } /* Literal.String.Escape */
    .codehilite .sh { color: #BA2121 } /* Literal.String.Herald */
    .codehilite .si { color: #BA2121 } /* Literal.String.Interpol */
    .codehilite .sx { color: #BA2121 } /* Literal.String.Other */
    .codehilite .sr { color: #BA2121 } /* Literal.String.Regex */
    .codehilite .s1 { color: #BA2121 } /* Literal.String.Single */
    .codehilite .ss { color: #BA2121 } /* Literal.String.Symbol */
    .codehilite .bp { color: #008000 } /* Name.Builtin.Pseudo */
    .codehilite .fm { color: #0000FF } /* Name.Function.Magic */
    .codehilite .vc { color: #19177C } /* Name.Variable.Class */
    .codehilite .vg { color: #19177C } /* Name.Variable.Global */
    .codehilite .vi { color: #19177C } /* Name.Variable.Instance */
    .codehilite .vm { color: #19177C } /* Name.Variable.Magic */
    .codehilite .il { color: #666666 } /* Literal.Number.Integer.Long */

    /* 响应式设计 */
    @media (max-width: 768px) {
        .preview-content {
            font-size: 16px;
            padding: 12px;
        }

        .preview-content h1 { font-size: 1.8em; }
        .preview-content h2 { font-size: 1.4em; }
        .preview-content h3 { font-size: 1.2em; }

        .preview-content pre {
            padding: 12px;
            font-size: 14px;
        }

        .preview-content table {
            font-size: 14px;
        }

        .preview-content th,
        .preview-content td {
            padding: 6px 8px;
        }
    }

    @media (max-width: 480px) {
        .preview-content {
            padding: 8px;
        }

        .preview-content h1 { font-size: 1.6em; }
        .preview-content h2 { font-size: 1.3em; }
        .preview-content h3 { font-size: 1.1em; }

        .preview-content pre {
            padding: 8px;
        }

        .preview-content th,
        .preview-content td {
            padding: 4px 6px;
        }
    }

    /* 打印样式 */
    @media print {
        body {
            background-color: white;
            color: black;
            max-width: none;
            padding: 0;
        }

        .preview-content {
            max-width: none;
            padding: 0;
        }

        pre {
            background-color: #f5f5f5;
            color: black;
            border: 1px solid #ccc;
        }

        a {
            color: black;
            text-decoration: underline;
        }
    }
    """

    # 生成文档标题（从第一个标题提取或使用默认标题）
    title = "Markdown 文档"
    lines = original_markdown.split('\n')
    for line in lines:
        if line.strip().startswith('# '):
            title = line.strip()[2:].strip()
            break

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
    {typography_themes_css}
    {code_themes_css}
    {css_styles}
    </style>
</head>
<body class="typography-classic code-github">
    <div class="preview-content">
    {html_content}
    </div>
</body>
</html>"""
    return html_template


def parse_list_structure(original_markdown):
    """解析列表结构"""
    lines = original_markdown.split('\n')
    list_items = []
    indent_stack = []

    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if not stripped:
            continue

        # 计算缩进级别
        indent_match = re.match(r'^(\s*)', line)
        indent_level = len(indent_match.group(1)) if indent_match else 0

        # 检查是否是列表项
        ul_match = re.match(r'^(\s*)[-\*\+]\s+(.+)$', line)
        ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)

        if ul_match or ol_match:
            # 计算列表级别 - 更精确的缩进检测
            list_level = 0
            if indent_level >= 2:
                list_level = (indent_level // 2)
            elif indent_level >= 1:
                list_level = 1

            # 确定列表类型
            list_type = 'ul' if ul_match else 'ol'
            content = ul_match.group(2) if ul_match else ol_match.group(2)

            item = {
                'level': list_level,
                'type': list_type,
                'content': content.strip(),
                'line_index': i,
                'children': []
            }

            # 处理嵌套关系 - 确保正确的父子关系
            while indent_stack and indent_stack[-1]['level'] >= list_level:
                indent_stack.pop()

            if indent_stack:
                indent_stack[-1]['children'].append(item)
            else:
                list_items.append(item)

            indent_stack.append(item)

        elif indent_stack and indent_level > indent_stack[-1]['level'] * 2:
            # 这是列表项的延续内容
            indent_stack[-1]['content'] += '\n' + stripped.lstrip()

    return list_items


def rebuild_html_with_proper_indentation(soup, list_structure):
    # 重新构建具有正确缩进的HTML
    def build_list_html(items, level=0):
        if not items:
            return ''

        # 按类型分组
        ul_items = [item for item in items if item['type'] == 'ul']
        ol_items = [item for item in items if item['type'] == 'ol']

        html_parts = []

        # 处理无序列表
        if ul_items:
            li_parts = []
            for item in ul_items:
                # 处理内容中的Markdown
                content_html = markdown.markdown(item['content'], extensions=['extra'])

                # 构建列表项HTML
                li_html = f'<li>{content_html.strip()}'

                # 添加子列表
                if item['children']:
                    child_html = build_list_html(item['children'], level + 1)
                    if child_html:
                        li_html += '\n' + child_html

                li_html += '</li>'
                li_parts.append(li_html)

            # 构建完整的列表
            list_html = '<ul>\n' + '\n'.join(li_parts) + '\n</ul>'
            html_parts.append(list_html)

        # 处理有序列表
        if ol_items:
            li_parts = []
            for item in ol_items:
                # 处理内容中的Markdown
                content_html = markdown.markdown(item['content'], extensions=['extra'])

                # 构建列表项HTML
                li_html = f'<li>{content_html.strip()}'

                # 添加子列表
                if item['children']:
                    child_html = build_list_html(item['children'], level + 1)
                    if child_html:
                        li_html += '\n' + child_html

                li_html += '</li>'
                li_parts.append(li_html)

            # 构建完整的列表
            list_html = '<ol>\n' + '\n'.join(li_parts) + '\n</ol>'
            html_parts.append(list_html)

        return '\n'.join(html_parts)

    # 替换原始的列表HTML
    for ul in soup.find_all('ul'):
        ul.decompose()
    for ol in soup.find_all('ol'):
        ol.decompose()

    # 添加新的正确缩进的列表
    if list_structure:
        new_list_html = build_list_html(list_structure)
        if new_list_html:
            # 在适当的位置插入新的列表
            body = soup.find('body')
            if body:
                # 使用BeautifulSoup解析新的HTML并保持格式
                new_soup = BeautifulSoup(new_list_html, 'html.parser')
                body.append(new_soup)

    # 返回格式化的HTML
    return soup.prettify()


def post_process_html_lists(html_content):
    # 后处理HTML以确保列表缩进正确
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 处理所有列表项，确保它们有正确的缩进结构
        def process_list_items(element, depth=0):
            # 递归处理列表项
            if element.name in ['ul', 'ol']:
                # 为列表添加深度类
                if depth > 0:
                    element['class'] = element.get('class', []) + [f'list-depth-{depth}']

                # 处理子列表项
                for li in element.find_all('li', recursive=False):
                    # 确保列表项有正确的结构
                    if not li.get('class'):
                        li['class'] = []
                    li['class'].append('list-item')

                    # 递归处理嵌套列表
                    for child in li.find_all(['ul', 'ol'], recursive=False):
                        process_list_items(child, depth + 1)

                return element

        # 处理所有顶级列表
        for ul in soup.find_all('ul', recursive=False):
            process_list_items(ul, 0)

        for ol in soup.find_all('ol', recursive=False):
            process_list_items(ol, 0)

        # 返回处理后的HTML
        return str(soup)

    except Exception as e:
        # 如果处理失败，返回原始内容
        print(f"列表后处理失败: {e}")
        return html_content


@markdown_tools_bp.route('/to-plain', methods=['POST'])
def markdown_to_plain():
    # Markdown转纯文本
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
    # 转义Markdown特殊字符
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
    # 反转义Markdown特殊字符
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
    # 提取Markdown中的链接
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
    # 提取Markdown中的图片
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
    # HTML表格转Markdown表格
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
    # 验证Markdown语法
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
    # Markdown文档统计
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
