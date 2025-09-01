from flask import Blueprint, request, jsonify
import qrcode
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import json

qr_tools_bp = Blueprint('qr_tools', __name__)

@qr_tools_bp.route('/generate', methods=['POST'])
def generate_qr():
    """生成二维码"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': '请提供content字段'}), 400

        content = data['content']
        size = data.get('size', 300)  # 二维码大小，默认300px
        color = data.get('color', 'black')  # 二维码颜色，默认黑色
        background = data.get('background', 'white')  # 背景颜色，默认白色

        try:
            # 创建二维码实例
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # 添加数据
            qr.add_data(content)
            qr.make(fit=True)

            # 创建二维码图像
            img = qr.make_image(fill_color=color, back_color=background)
            
            # 调整大小
            img = img.resize((size, size), Image.LANCZOS)

            # 将图像转换为base64编码
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return jsonify({
                'success': True,
                'qr_code': img_str,
                'content': content,
                'size': size,
                'format': 'png'
            }), 200

        except Exception as e:
            return jsonify({'error': f'生成二维码失败: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_tools_bp.route('/beautify', methods=['POST'])
def beautify_qr():
    """美化二维码"""
    try:
        data = request.get_json()
        if not data or 'qr_code' not in data:
            return jsonify({'error': '请提供qr_code字段'}), 400

        qr_base64 = data['qr_code']
        logo = data.get('logo')  # 可选的logo base64
        border_color = data.get('border_color', 'black')  # 边框颜色
        border_width = data.get('border_width', 0)  # 边框宽度
        corner_radius = data.get('corner_radius', 0)  # 圆角半径

        try:
            # 解码base64图像
            img_data = base64.b64decode(qr_base64)
            img = Image.open(io.BytesIO(img_data))
            
            # 添加圆角
            if corner_radius > 0:
                img = add_rounded_corners(img, corner_radius)
            
            # 添加边框
            if border_width > 0:
                img = add_border(img, border_color, border_width)
            
            # 添加logo
            if logo:
                img = add_logo(img, logo)

            # 将图像转换为base64编码
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return jsonify({
                'success': True,
                'beautified_qr_code': img_str,
                'border_color': border_color,
                'border_width': border_width,
                'corner_radius': corner_radius
            }), 200

        except Exception as e:
            return jsonify({'error': f'美化二维码失败: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def add_rounded_corners(img, radius):
    """添加圆角"""
    # 创建圆角遮罩
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # 绘制圆角矩形
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    
    # 应用遮罩
    img.putalpha(mask)
    return img

def add_border(img, color, width):
    """添加边框"""
    # 创建新图像
    new_size = (img.size[0] + 2 * width, img.size[1] + 2 * width)
    bordered_img = Image.new('RGBA', new_size, color)
    
    # 粘贴原图像
    bordered_img.paste(img, (width, width))
    return bordered_img

def add_logo(img, logo_base64):
    """添加logo"""
    try:
        # 解码logo
        logo_data = base64.b64decode(logo_base64)
        logo = Image.open(io.BytesIO(logo_data))
        
        # 调整logo大小（设为二维码大小的1/4）
        logo_size = min(img.size) // 4
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        
        # 计算logo位置（居中）
        img_width, img_height = img.size
        logo_width, logo_height = logo.size
        position = ((img_width - logo_width) // 2, (img_height - logo_height) // 2)
        
        # 粘贴logo
        img.paste(logo, position, logo)
        return img
    except Exception as e:
        # 如果添加logo失败，返回原图像
        return img
