"""
Shared CSS styles for data conversion HTML/PDF rendering.

This module centralizes the duplicated CSS that was previously inlined
across multiple functions in data_conversion.py (markdown_to_html,
markdown_to_pdf_weasyprint, markdown_to_pdf_wkhtmltopdf, html_to_pdf,
and preview_markdown).
"""


def get_base_css():
    """Return the base CSS string used for PDF generation and standalone HTML.

    This CSS uses hardcoded color values (no CSS variables) for maximum
    compatibility with PDF renderers (WeasyPrint, wkhtmltopdf).
    """
    return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: #334155;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background-color: #ffffff;
            tab-size: 4;
        }

        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }

        h1 {
            font-size: 2.5em;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }

        h2 {
            font-size: 2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 12px;
            margin-top: 40px;
        }

        h3 {
            font-size: 1.75em;
            color: #1e293b;
            margin-top: 35px;
        }

        h4 {
            font-size: 1.5em;
            color: #334155;
            margin-top: 30px;
        }

        h5 {
            font-size: 1.25em;
            color: #475569;
            margin-top: 25px;
        }

        h6 {
            font-size: 1.1em;
            color: #64748b;
            margin-top: 20px;
        }

        /* 段落样式 */
        p {
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.05em;
            text-align: justify;
        }

        /* 链接样式 */
        a {
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
        }

        a:hover {
            color: #1d4ed8;
            border-bottom: 1px solid #1d4ed8;
        }

        /* 代码样式 */
        code {
            padding: 0.3em 0.5em;
            margin: 0 0.2em;
            font-size: 0.9em;
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }

        pre {
            padding: 20px;
            overflow: auto;
            font-size: 0.95em;
            line-height: 1.5;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 25px 0;
            border: 1px solid #e2e8f0;
        }

        pre code {
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }

        /* 引用块样式 */
        blockquote {
            padding: 20px 25px;
            margin: 25px 0;
            color: #475569;
            border-left: 5px solid #2563eb;
            background-color: #f1f5f9;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        blockquote p {
            margin: 0;
            font-style: italic;
        }

        blockquote::before {
            content: "\\201C";
            font-size: 3em;
            color: #2563eb;
            opacity: 0.3;
            line-height: 0.1em;
            margin-right: 0.25em;
            vertical-align: -0.4em;
        }

        /* 列表样式 */
        ul, ol {
            padding-left: 2.5em;
            margin: 20px 0;
        }

        li {
            margin-bottom: 10px;
            line-height: 1.7;
        }

        ul li {
            list-style-type: disc;
        }

        ul ul li {
            list-style-type: circle;
        }

        ul ul ul li {
            list-style-type: square;
        }

        ol li {
            list-style-type: decimal;
        }

        /* 嵌套列表处理 */
        ul ul, ul ol, ol ul, ol ol {
            margin-top: 10px;
            margin-bottom: 10px;
        }

        li > p {
            margin-top: 0;
            margin-bottom: 0;
        }

        /* 表格样式 */
        table {
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        table th, table td {
            padding: 12px 15px;
            border: 1px solid #e2e8f0;
        }

        table th {
            background-color: #f1f5f9;
            font-weight: 600;
            text-align: left;
            color: #1e293b;
        }

        table tr:nth-child(2n) {
            background-color: #f8fafc;
        }

        table tr:hover {
            background-color: #e0f2fe;
        }

        /* 分隔线样式 */
        hr {
            height: 2px;
            padding: 0;
            margin: 40px 0;
            background: linear-gradient(to right, transparent, #2563eb, transparent);
            border: 0;
        }

        /* 图片样式 */
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }

        /* 内联代码高亮 */
        p code {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-weight: 500;
        }
    """


def get_css_variables():
    """Return the :root CSS variable declarations used by the full HTML template."""
    return """
        :root {
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
        }
    """


def get_responsive_css():
    """Return responsive CSS media queries for mobile devices."""
    return """
        /* 响应式设计 */
        @media (max-width: 768px) {
            body {
                padding: 20px;
                font-size: 0.95em;
            }

            h1 {
                font-size: 2em;
            }

            h2 {
                font-size: 1.7em;
            }

            h3 {
                font-size: 1.5em;
            }

            pre {
                padding: 15px;
                font-size: 0.85em;
            }
        }
    """


def get_print_css():
    """Return print media CSS for proper printing/PDF output."""
    return """
        /* 打印样式 */
        @media print {
            body {
                padding: 20px;
                max-width: 100%;
            }

            pre {
                box-shadow: none;
                border: 1px solid #ccc;
            }

            blockquote {
                box-shadow: none;
                border: 1px solid #ccc;
            }

            table {
                box-shadow: none;
                border: 1px solid #ccc;
            }
        }
    """


def get_enhanced_base_css():
    """Return the enhanced base CSS that uses CSS variables.

    This is the variant used by markdown_to_html() which leverages
    CSS custom properties (var()) for theming support.
    """
    return get_css_variables() + _get_body_and_typography_css_with_vars()


def _get_body_and_typography_css_with_vars():
    """Return body + typography + all element CSS using CSS variables.

    This is the CSS used by markdown_to_html() -- identical structure
    to get_base_css() but with var() references instead of hardcoded colors.
    """
    return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: var(--text-color);
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background-color: var(--background-color);
            tab-size: 4;
        }

        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }

        h1 {
            font-size: 2.5em;
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 15px;
            margin-bottom: 30px;
        }

        h2 {
            font-size: 2em;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 12px;
            margin-top: 40px;
        }

        h3 {
            font-size: 1.75em;
            color: #1e293b;
            margin-top: 35px;
        }

        h4 {
            font-size: 1.5em;
            color: #334155;
            margin-top: 30px;
        }

        h5 {
            font-size: 1.25em;
            color: #475569;
            margin-top: 25px;
        }

        h6 {
            font-size: 1.1em;
            color: #64748b;
            margin-top: 20px;
        }

        /* 段落样式 */
        p {
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 1.05em;
            text-align: justify;
        }

        /* 链接样式 */
        a {
            color: var(--link-color);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s ease;
        }

        a:hover {
            color: var(--link-hover);
            border-bottom: 1px solid var(--link-hover);
        }

        /* 代码样式 */
        code {
            padding: 0.3em 0.5em;
            margin: 0 0.2em;
            font-size: 0.9em;
            background-color: var(--code-background);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }

        pre {
            padding: 20px;
            overflow: auto;
            font-size: 0.95em;
            line-height: 1.5;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin: 25px 0;
            border: 1px solid var(--border-color);
        }

        pre code {
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }

        /* 引用块样式 */
        blockquote {
            padding: 20px 25px;
            margin: 25px 0;
            color: #475569;
            border-left: 5px solid var(--primary-color);
            background-color: var(--blockquote-background);
            border-radius: 0 8px 8px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        blockquote p {
            margin: 0;
            font-style: italic;
        }

        blockquote::before {
            content: "\\201C";
            font-size: 3em;
            color: var(--primary-color);
            opacity: 0.3;
            line-height: 0.1em;
            margin-right: 0.25em;
            vertical-align: -0.4em;
        }

        /* 列表样式 */
        ul, ol {
            padding-left: 2.5em;
            margin: 20px 0;
        }

        li {
            margin-bottom: 10px;
            line-height: 1.7;
        }

        ul li {
            list-style-type: disc;
        }

        ul ul li {
            list-style-type: circle;
        }

        ul ul ul li {
            list-style-type: square;
        }

        ol li {
            list-style-type: decimal;
        }

        /* 嵌套列表处理 */
        ul ul, ul ol, ol ul, ol ol {
            margin-top: 10px;
            margin-bottom: 10px;
        }

        li > p {
            margin-top: 0;
            margin-bottom: 0;
        }

        /* 特别处理列表项中的换行 */
        li br {
            display: inline;
        }

        /* 表格样式 */
        table {
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        table th, table td {
            padding: 12px 15px;
            border: 1px solid var(--border-color);
        }

        table th {
            background-color: var(--table-header);
            font-weight: 600;
            text-align: left;
            color: #1e293b;
        }

        table tr:nth-child(2n) {
            background-color: var(--table-row-even);
        }

        table tr:hover {
            background-color: #e0f2fe;
        }

        /* 分隔线样式 */
        hr {
            height: 2px;
            padding: 0;
            margin: 40px 0;
            background: linear-gradient(to right, transparent, var(--primary-color), transparent);
            border: 0;
        }

        /* 图片样式 */
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }

        /* 内联代码高亮 */
        p code {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-weight: 500;
        }
    """


def get_preview_css():
    """Return the scoped CSS for .markdown-preview inline preview.

    This CSS is scoped under the .markdown-preview class and uses
    slightly different spacing/sizing values optimized for inline
    preview rendering rather than full-page or PDF output.
    """
    return """
        .markdown-preview {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.7;
            color: #334155;
            max-width: 100%;
            padding: 20px;
            background-color: #ffffff;
        }

        .markdown-preview h1,
        .markdown-preview h2,
        .markdown-preview h3,
        .markdown-preview h4,
        .markdown-preview h5,
        .markdown-preview h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 700;
            line-height: 1.25;
            color: #0f172a;
        }

        .markdown-preview h1 {
            font-size: 2em;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.3em;
        }

        .markdown-preview h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.3em;
        }

        .markdown-preview h3 {
            font-size: 1.25em;
        }

        .markdown-preview p {
            margin-top: 0;
            margin-bottom: 16px;
            text-align: justify;
        }

        .markdown-preview a {
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: all 0.3s ease;
        }

        .markdown-preview a:hover {
            color: #1d4ed8;
            border-bottom: 1px solid #1d4ed8;
        }

        .markdown-preview code {
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            white-space: pre-wrap;
            color: #d63384;
        }

        .markdown-preview pre {
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
        }

        .markdown-preview pre code {
            padding: 0;
            margin: 0;
            overflow: visible;
            font-size: 100%;
            word-wrap: normal;
            background-color: transparent;
            border: 0;
            white-space: pre-wrap;
            color: #333;
        }

        .markdown-preview blockquote {
            padding: 0 1em;
            color: #64748b;
            border-left: 0.25em solid #2563eb;
            background-color: #f1f5f9;
            border-radius: 0 4px 4px 0;
            margin: 16px 0;
        }

        .markdown-preview ul,
        .markdown-preview ol {
            padding-left: 2em;
            margin-top: 0;
            margin-bottom: 16px;
        }

        .markdown-preview li {
            margin-bottom: 0.25em;
            line-height: 1.5;
        }

        .markdown-preview ul ul,
        .markdown-preview ul ol,
        .markdown-preview ol ul,
        .markdown-preview ol ol {
            margin-top: 0;
            margin-bottom: 0;
        }

        .markdown-preview li > p {
            margin-top: 0;
            margin-bottom: 0;
        }

        .markdown-preview table {
            display: block;
            width: 100%;
            overflow: auto;
            border-collapse: collapse;
            margin: 16px 0;
        }

        .markdown-preview table th,
        .markdown-preview table td {
            padding: 6px 13px;
            border: 1px solid #e2e8f0;
        }

        .markdown-preview table th {
            background-color: #f1f5f9;
            font-weight: 600;
        }

        .markdown-preview table tr:nth-child(2n) {
            background-color: #f8fafc;
        }

        .markdown-preview hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e2e8f0;
            border: 0;
        }

        .markdown-preview img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
    """


def build_full_html(body_html, title="Markdown转换结果", use_vars=False):
    """Build a complete HTML document with CSS styling.

    Args:
        body_html: The HTML content to wrap in the body.
        title: The page title (default: 'Markdown转换结果').
        use_vars: If True, use CSS variables for theming support
                  (used by markdown_to_html). If False, use hardcoded
                  colors (used by PDF generation functions).

    Returns:
        A complete HTML document string.
    """
    if use_vars:
        css = get_enhanced_base_css() + get_responsive_css() + get_print_css()
    else:
        css = get_base_css()

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}
    </style>
</head>
<body>
    <article>
        {body_html}
    </article>
</body>
</html>"""


def build_preview_html(body_html):
    """Build an inline preview HTML fragment with scoped CSS.

    This wraps the content in a .markdown-preview div with scoped styles,
    suitable for embedding in an existing page.

    Args:
        body_html: The rendered HTML content to preview.

    Returns:
        An HTML fragment string with inline styles.
    """
    return f"""<div class="markdown-preview">
    <style>{get_preview_css()}
    </style>
    {body_html}
</div>"""
