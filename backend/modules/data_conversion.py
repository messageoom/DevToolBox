from flask import Blueprint, request, jsonify, send_file
import markdown
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

        # 转换Markdown为HTML
        html_content = markdown.markdown(
            markdown_text,
            extensions=[
                'extra',
                'codehilite',
                'toc',
                'fenced_code',
                'tables',
                'nl2br'
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
    """Markdown转PDF"""
    pdf_filename = None
    try:
        data = request.get_json()
        if not data or 'markdown_text' not in data:
            return jsonify({'error': '请提供markdown_text字段'}), 400

        markdown_text = data['markdown_text']
        if not markdown_text.strip():
            return jsonify({'error': 'Markdown文本不能为空'}), 400

        # 创建临时PDF文件
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_filename = tmp_file.name
        tmp_file.close()  # 关闭文件句柄，让其他进程可以访问

        # 注册中文字体
        try:
            # 尝试注册系统中文字体
            pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
            pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'C:/Windows/Fonts/msyh.ttc'))
        except:
            # 如果无法注册系统字体，使用默认字体
            pass

        # 创建PDF文档
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        styles = getSampleStyleSheet()

        # 定义样式
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        
        # 标题样式
        heading1_style = ParagraphStyle(
            'Heading1',
            parent=styles['Heading1'],
            fontName='SimSun',
            fontSize=16,
            leading=20,
            spaceBefore=12,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        # 二级标题样式
        heading2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontName='SimSun',
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=4,
            alignment=TA_LEFT
        )
        
        # 三级标题样式
        heading3_style = ParagraphStyle(
            'Heading3',
            parent=styles['Heading3'],
            fontName='SimSun',
            fontSize=13,
            leading=17,
            spaceBefore=8,
            spaceAfter=4,
            alignment=TA_LEFT
        )
        
        # 正文样式
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName='SimSun',
            fontSize=12,
            leading=16,
            alignment=TA_LEFT
        )
        
        # 一级列表样式（不缩进）
        list1_style = ParagraphStyle(
            'List1',
            parent=normal_style,
            fontName='SimSun',
            fontSize=12,
            leading=16,
            alignment=TA_LEFT
        )
        
        # 二级列表样式（缩进4个空格）
        list2_style = ParagraphStyle(
            'List2',
            parent=normal_style,
            fontName='SimSun',
            fontSize=12,
            leading=16,
            leftIndent=20,
            alignment=TA_LEFT
        )
        
        # 三级列表样式（缩进8个空格）
        list3_style = ParagraphStyle(
            'List3',
            parent=normal_style,
            fontName='SimSun',
            fontSize=12,
            leading=16,
            leftIndent=40,
            alignment=TA_LEFT
        )

        # 将Markdown转换为HTML以便解析结构
        html_content = markdown.markdown(
            markdown_text,
            extensions=[
                'extra',
                'codehilite',
                'fenced_code',
                'tables',
                'nl2br'
            ]
        )
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # PDF元素列表
        pdf_elements = []
        
        # 中文数字映射
        chinese_nums = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
        
        # 第一次扫描，查找所有一级标题
        lines = markdown_text.split('\n')
        h1_titles = []  # 存储所有一级标题
        
        for line in lines:
            h1_match = re.match(r'^###\s+(.*?)$', line)
            if h1_match:
                title = h1_match.group(1).strip()
                # 移除可能的粗体标记
                title = re.sub(r'\*\*(.*?)\*\*', r'\1', title)
                h1_titles.append(title)
        
        # 追踪标题编号
        h1_processed_count = 0  # 已处理的一级标题数量
        h2_counters = {}
        
        # 处理Markdown文本行
        i = 0
        current_h2_index = None
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # 处理一级标题 (### 开头)
            h1_match = re.match(r'^###\s+(.*?)$', line)
            if h1_match:
                title_text = h1_match.group(1).strip()
                # 删除粗体标记
                title_text = re.sub(r'\*\*(.*?)\*\*', r'\1', title_text)
                # 删除可能存在的数字前缀（包括中文序号前缀）
                title_text = re.sub(r'^\d+\.\d+\s+', '', title_text)
                # 删除可能存在的中文序号前缀（包括重复的）
                title_text = re.sub(r'^(?:[一二三四五六七八九]\s*、\s*)+', '', title_text)
                    
                # 确保每个一级标题都有唯一的序号
                if h1_processed_count < len(chinese_nums):
                    chinese_num = chinese_nums[h1_processed_count]
                else:
                    chinese_num = str(h1_processed_count + 1)
                    
                pdf_elements.append(Paragraph(f"{chinese_num}、{title_text}", heading1_style))
                pdf_elements.append(Spacer(1, 8))
                    
                # 增加已处理的一级标题计数
                h1_processed_count += 1
                    
                i += 1
                continue
            
            # 处理二级标题（通常是粗体的数字列表项）
            h2_bold_match = re.match(r'^(\d+)\.\s+\*\*(.+?)\*\*$', line)
            h2_normal_match = re.match(r'^(\d+)\.\s+(.+?)$', line)
            if h2_bold_match:
                number = int(h2_bold_match.group(1))
                title = h2_bold_match.group(2)
                
                # 确保标题与当前一级标题相关联
                pdf_elements.append(Paragraph(f"{number}. {title}", heading2_style))
                pdf_elements.append(Spacer(1, 6))
                
                # 更新当前二级标题索引
                current_h2_index = number
                
                i += 1
                continue
            elif h2_normal_match and i > 0 and re.match(r'^###', lines[i-1]):
                # 处理紧跟一级标题的非粗体数字列表项作为二级标题
                number = int(h2_normal_match.group(1))
                title = h2_normal_match.group(2)
                
                # 删除粗体标记
                title = re.sub(r'\*\*(.*?)\*\*', r'\1', title)
                
                # 更新当前二级标题索引
                current_h2_index = number
                
                pdf_elements.append(Paragraph(f"{number}. {title}", heading2_style))
                pdf_elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # 处理普通一级列表项
            list1_match = re.match(r'^(\d+)\.\s+(.+?)$', line)
            if list1_match and not re.search(r'\*\*', line):
                number = int(list1_match.group(1))
                content = list1_match.group(2)
                
                # 删除粗体标记
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                
                pdf_elements.append(Paragraph(f"{number}. {content}", list1_style))
                pdf_elements.append(Spacer(1, 4))
                i += 1
                continue
            
            # 处理二级列表项（缩进的无序列表）
            list2_match = re.match(r'^(\s{2,4}|  |\t)([-*•]\s+)(.+?)$', line)
            if list2_match:
                content = list2_match.group(3).strip()
                
                # 删除粗体标记
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                
                pdf_elements.append(Paragraph(f"    • {content}", list2_style))
                pdf_elements.append(Spacer(1, 2))
                i += 1
                continue
            
            # 处理二级列表项（缩进的有序列表）
            list2_ordered_match = re.match(r'^(\s{2,4}|  |\t)(\d+)\.\s+(.+?)$', line)
            if list2_ordered_match:
                number = int(list2_ordered_match.group(2))
                content = list2_ordered_match.group(3).strip()
                
                # 删除粗体标记
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                
                pdf_elements.append(Paragraph(f"    ({number}) {content}", list2_style))
                pdf_elements.append(Spacer(1, 2))
                i += 1
                continue
            
            # 处理三级列表项（更多缩进的无序列表）
            list3_match = re.match(r'^(\s{6,8}|\t\t|        )([-*•◦]\s+)(.+?)$', line)
            if list3_match:
                content = list3_match.group(3).strip()
                
                # 删除粗体标记
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                
                pdf_elements.append(Paragraph(f"        ◦ {content}", list3_style))
                pdf_elements.append(Spacer(1, 2))
                i += 1
                continue
            
            # 处理三级列表项（更多缩进的有序列表）
            list3_ordered_match = re.match(r'^(\s{6,8}|\t\t|        )(\d+)\.\s+(.+?)$', line)
            if list3_ordered_match:
                number = int(list3_ordered_match.group(2))
                content = list3_ordered_match.group(3).strip()
                
                # 删除粗体标记
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
                
                # 使用带圈数字
                circled_numbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
                if 1 <= number <= 10:
                    number_marker = circled_numbers[number-1]
                else:
                    number_marker = f"{number}."
                
                pdf_elements.append(Paragraph(f"        {number_marker} {content}", list3_style))
                pdf_elements.append(Spacer(1, 2))
                i += 1
                continue
                
            # 处理分隔线
            if line == '---':
                pdf_elements.append(Spacer(1, 10))
                i += 1
                continue
                
            # 处理空行
            if not line.strip():
                pdf_elements.append(Spacer(1, 4))
                i += 1
                continue
                
            # 处理普通文本
            # 删除粗体标记
            line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            
            pdf_elements.append(Paragraph(line, normal_style))
            pdf_elements.append(Spacer(1, 4))
            i += 1
        
        # 生成PDF
        doc.build(pdf_elements)

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
        return jsonify({'error': str(e)}), 500

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
