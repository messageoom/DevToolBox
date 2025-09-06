from flask import Blueprint, request, jsonify
import base64
import json

# 尝试导入加密库
try:
    from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError as e:
    HAS_CRYPTOGRAPHY = False
    print(f"导入cryptography库失败: {e}")
    rsa = ec = ed25519 = hashes = serialization = asymmetric_padding = None
    algorithms = modes = padding = default_backend = None

try:
    from gmssl import sm2, sm4
    HAS_GMSSL = True
    
    # 尝试导入hex_to_bytes和bytes_to_hex函数
    try:
        from gmssl.func import hex_to_bytes, bytes_to_hex
    except ImportError:
        # 如果导入失败，使用自定义实现
        def hex_to_bytes(hex_str):
            return bytes.fromhex(hex_str)
        
        def bytes_to_hex(data):
            return data.hex()
except ImportError as e:
    HAS_GMSSL = False
    print(f"导入gmssl库失败: {e}")
    sm2 = sm4 = None
    # 提供兼容性函数
    def hex_to_bytes(hex_str):
        return bytes.fromhex(hex_str)

    def bytes_to_hex(data):
        return data.hex()

crypto_tools_bp = Blueprint('crypto_tools', __name__)

def get_error_response(message, status_code=400):
    """生成错误响应"""
    return jsonify({'error': message}), status_code

@crypto_tools_bp.route('/algorithms', methods=['GET'])
def get_algorithms():
    """获取支持的加密算法"""
    algorithms = {
        'asymmetric': [],
        'symmetric': []
    }

    if HAS_CRYPTOGRAPHY:
        algorithms['asymmetric'].extend(['RSA', 'ECC', 'Ed25519'])
        algorithms['symmetric'].extend(['AES', 'ChaCha20'])

    if HAS_GMSSL:
        algorithms['asymmetric'].append('SM2')
        algorithms['symmetric'].append('SM4')
    else:
        # 即使gmssl库不可用，也在前端显示这些算法（但会显示错误提示）
        algorithms['asymmetric'].append('SM2')
        algorithms['symmetric'].append('SM4')

    return jsonify({
        'success': True,
        'algorithms': algorithms,
        'has_cryptography': HAS_CRYPTOGRAPHY,
        'has_gmssl': HAS_GMSSL
    }), 200

# RSA相关功能
@crypto_tools_bp.route('/rsa/generate', methods=['POST'])
def generate_rsa_keypair():
    """生成RSA密钥对"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        key_size = data.get('key_size', 2048)
        
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # 获取公钥
        public_key = private_key.public_key()
        
        # 序列化私钥
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # 序列化公钥
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return jsonify({
            'success': True,
            'private_key': private_pem.decode('utf-8'),
            'public_key': public_pem.decode('utf-8'),
            'key_size': key_size
        }), 200
        
    except Exception as e:
        return get_error_response(f'生成RSA密钥对失败: {str(e)}')

@crypto_tools_bp.route('/rsa/encrypt', methods=['POST'])
def rsa_encrypt():
    """RSA加密"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'plaintext' not in data or 'public_key' not in data:
            return get_error_response('请提供plaintext和public_key字段')
        
        plaintext = data['plaintext']
        public_key_pem = data['public_key']
        encoding = data.get('encoding', 'utf-8')
        
        # 加载公钥
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        # 加密
        ciphertext = public_key.encrypt(
            plaintext.encode(encoding),
            asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return jsonify({
            'success': True,
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'plaintext_length': len(plaintext),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'RSA加密失败: {str(e)}')

@crypto_tools_bp.route('/rsa/decrypt', methods=['POST'])
def rsa_decrypt():
    """RSA解密"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'ciphertext' not in data or 'private_key' not in data:
            return get_error_response('请提供ciphertext和private_key字段')
        
        ciphertext = base64.b64decode(data['ciphertext'])
        private_key_pem = data['private_key']
        encoding = data.get('encoding', 'utf-8')
        
        # 加载私钥
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # 解密
        plaintext = private_key.decrypt(
            ciphertext,
            asymmetric_padding.OAEP(
                mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return jsonify({
            'success': True,
            'plaintext': plaintext.decode(encoding),
            'ciphertext_length': len(ciphertext),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'RSA解密失败: {str(e)}')

# ECC相关功能
@crypto_tools_bp.route('/ecc/generate', methods=['POST'])
def generate_ecc_keypair():
    """生成ECC密钥对"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        curve_name = data.get('curve', 'secp256r1')
        
        # 根据曲线名称选择曲线
        curves = {
            'secp256r1': ec.SECP256R1(),
            'secp384r1': ec.SECP384R1(),
            'secp521r1': ec.SECP521R1()
        }
        
        if curve_name not in curves:
            return get_error_response(f'不支持的曲线: {curve_name}')
        
        curve = curves[curve_name]
        
        # 生成私钥
        private_key = ec.generate_private_key(curve, default_backend())
        
        # 获取公钥
        public_key = private_key.public_key()
        
        # 序列化私钥
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # 序列化公钥
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return jsonify({
            'success': True,
            'private_key': private_pem.decode('utf-8'),
            'public_key': public_pem.decode('utf-8'),
            'curve': curve_name
        }), 200
        
    except Exception as e:
        return get_error_response(f'生成ECC密钥对失败: {str(e)}')

# Ed25519相关功能
@crypto_tools_bp.route('/ed25519/generate', methods=['POST'])
def generate_ed25519_keypair():
    """生成Ed25519密钥对"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        # 生成私钥
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        # 获取公钥
        public_key = private_key.public_key()
        
        # 序列化私钥
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # 序列化公钥
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return jsonify({
            'success': True,
            'private_key': base64.b64encode(private_bytes).decode('utf-8'),
            'public_key': base64.b64encode(public_bytes).decode('utf-8')
        }), 200
        
    except Exception as e:
        return get_error_response(f'生成Ed25519密钥对失败: {str(e)}')

@crypto_tools_bp.route('/ed25519/sign', methods=['POST'])
def ed25519_sign():
    """Ed25519签名"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'message' not in data or 'private_key' not in data:
            return get_error_response('请提供message和private_key字段')
        
        message = data['message']
        private_key_b64 = data['private_key']
        encoding = data.get('encoding', 'utf-8')
        
        # 加载私钥
        private_bytes = base64.b64decode(private_key_b64)
        private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes)
        
        # 签名
        signature = private_key.sign(message.encode(encoding))
        
        return jsonify({
            'success': True,
            'signature': base64.b64encode(signature).decode('utf-8'),
            'message_length': len(message),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'Ed25519签名失败: {str(e)}')

@crypto_tools_bp.route('/ed25519/verify', methods=['POST'])
def ed25519_verify():
    """Ed25519验证签名"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'message' not in data or 'signature' not in data or 'public_key' not in data:
            return get_error_response('请提供message、signature和public_key字段')
        
        message = data['message']
        signature_b64 = data['signature']
        public_key_b64 = data['public_key']
        encoding = data.get('encoding', 'utf-8')
        
        # 加载公钥
        public_bytes = base64.b64decode(public_key_b64)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
        
        # 加载签名
        signature = base64.b64decode(signature_b64)
        
        # 验证签名
        try:
            public_key.verify(signature, message.encode(encoding))
            is_valid = True
        except Exception:
            is_valid = False
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message_length': len(message),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'Ed25519验证签名失败: {str(e)}')

# AES相关功能
@crypto_tools_bp.route('/aes/encrypt', methods=['POST'])
def aes_encrypt():
    """AES加密"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'plaintext' not in data or 'key' not in data:
            return get_error_response('请提供plaintext和key字段')
        
        plaintext = data['plaintext']
        key_b64 = data['key']
        mode = data.get('mode', 'CBC')
        encoding = data.get('encoding', 'utf-8')
        
        # 解码密钥
        key = base64.b64decode(key_b64)
        
        # 检查密钥长度
        if len(key) not in [16, 24, 32]:
            return get_error_response('密钥长度必须为16、24或32字节')
        
        # 生成随机IV
        from os import urandom
        iv = urandom(16)
        
        # 选择算法和模式
        algorithm = algorithms.AES(key)
        if mode == 'CBC':
            cipher_mode = modes.CBC(iv)
        elif mode == 'ECB':
            cipher_mode = modes.ECB()
            iv = None
        elif mode == 'CFB':
            cipher_mode = modes.CFB(iv)
        elif mode == 'OFB':
            cipher_mode = modes.OFB(iv)
        else:
            return get_error_response(f'不支持的模式: {mode}')
        
        # 创建加密器
        cipher = Cipher(algorithm, cipher_mode, backend=default_backend())
        encryptor = cipher.encryptor()
        
        # 填充明文（对于CBC、ECB模式）
        if mode in ['CBC', 'ECB']:
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext.encode(encoding)) + padder.finalize()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        else:
            ciphertext = encryptor.update(plaintext.encode(encoding)) + encryptor.finalize()
        
        # 返回结果
        result = {
            'success': True,
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'mode': mode,
            'plaintext_length': len(plaintext),
            'encoding': encoding
        }
        
        if iv:
            result['iv'] = base64.b64encode(iv).decode('utf-8')
        
        return jsonify(result), 200
        
    except Exception as e:
        return get_error_response(f'AES加密失败: {str(e)}')

@crypto_tools_bp.route('/aes/decrypt', methods=['POST'])
def aes_decrypt():
    """AES解密"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'ciphertext' not in data or 'key' not in data:
            return get_error_response('请提供ciphertext和key字段')
        
        ciphertext_b64 = data['ciphertext']
        key_b64 = data['key']
        mode = data.get('mode', 'CBC')
        iv_b64 = data.get('iv')
        encoding = data.get('encoding', 'utf-8')
        
        # 解码密钥和密文
        key = base64.b64decode(key_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        
        # 检查密钥长度
        if len(key) not in [16, 24, 32]:
            return get_error_response('密钥长度必须为16、24或32字节')
        
        # 解码IV（如果提供）
        iv = base64.b64decode(iv_b64) if iv_b64 else None
        
        # 选择算法和模式
        algorithm = algorithms.AES(key)
        if mode == 'CBC':
            if not iv or len(iv) != 16:
                return get_error_response('CBC模式需要16字节IV')
            cipher_mode = modes.CBC(iv)
        elif mode == 'ECB':
            cipher_mode = modes.ECB()
        elif mode == 'CFB':
            if not iv or len(iv) != 16:
                return get_error_response('CFB模式需要16字节IV')
            cipher_mode = modes.CFB(iv)
        elif mode == 'OFB':
            if not iv or len(iv) != 16:
                return get_error_response('OFB模式需要16字节IV')
            cipher_mode = modes.OFB(iv)
        else:
            return get_error_response(f'不支持的模式: {mode}')
        
        # 创建解密器
        cipher = Cipher(algorithm, cipher_mode, backend=default_backend())
        decryptor = cipher.decryptor()
        
        # 解密
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 去除填充（对于CBC、ECB模式）
        if mode in ['CBC', 'ECB']:
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(decrypted_data) + unpadder.finalize()
        else:
            plaintext = decrypted_data
        
        return jsonify({
            'success': True,
            'plaintext': plaintext.decode(encoding),
            'ciphertext_length': len(ciphertext),
            'mode': mode,
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'AES解密失败: {str(e)}')

# ChaCha20相关功能
@crypto_tools_bp.route('/chacha20/encrypt', methods=['POST'])
def chacha20_encrypt():
    """ChaCha20加密"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'plaintext' not in data or 'key' not in data:
            return get_error_response('请提供plaintext和key字段')
        
        plaintext = data['plaintext']
        key_b64 = data['key']
        encoding = data.get('encoding', 'utf-8')
        
        # 解码密钥
        key = base64.b64decode(key_b64)
        
        # 检查密钥长度
        if len(key) != 32:
            return get_error_response('ChaCha20密钥长度必须为32字节')
        
        # 生成随机nonce
        from os import urandom
        nonce = urandom(16)
        
        # 创建加密器
        algorithm = algorithms.ChaCha20(key, nonce)
        cipher = Cipher(algorithm, mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        
        # 加密
        ciphertext = encryptor.update(plaintext.encode(encoding)) + encryptor.finalize()
        
        return jsonify({
            'success': True,
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'plaintext_length': len(plaintext),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'ChaCha20加密失败: {str(e)}')

@crypto_tools_bp.route('/chacha20/decrypt', methods=['POST'])
def chacha20_decrypt():
    """ChaCha20解密"""
    if not HAS_CRYPTOGRAPHY:
        return get_error_response('cryptography库未安装')
    
    try:
        data = request.get_json()
        if not data or 'ciphertext' not in data or 'key' not in data or 'nonce' not in data:
            return get_error_response('请提供ciphertext、key和nonce字段')
        
        ciphertext_b64 = data['ciphertext']
        key_b64 = data['key']
        nonce_b64 = data['nonce']
        encoding = data.get('encoding', 'utf-8')
        
        # 解码密钥、密文和nonce
        key = base64.b64decode(key_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        
        # 检查密钥长度
        if len(key) != 32:
            return get_error_response('ChaCha20密钥长度必须为32字节')
        
        # 检查nonce长度
        if len(nonce) != 16:
            return get_error_response('ChaCha20 nonce长度必须为16字节')
        
        # 创建解密器
        algorithm = algorithms.ChaCha20(key, nonce)
        cipher = Cipher(algorithm, mode=None, backend=default_backend())
        decryptor = cipher.decryptor()
        
        # 解密
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return jsonify({
            'success': True,
            'plaintext': plaintext.decode(encoding),
            'ciphertext_length': len(ciphertext),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'ChaCha20解密失败: {str(e)}')

# SM2相关功能
@crypto_tools_bp.route('/sm2/generate', methods=['POST'])
def generate_sm2_keypair():
    """生成SM2密钥对"""
    if not HAS_GMSSL:
        return get_error_response('gmssl库未安装')
    
    try:
        # 生成SM2密钥对
        sk, pk = sm2.sm2_key_pair_gen()
        
        return jsonify({
            'success': True,
            'private_key': sk,
            'public_key': pk
        }), 200
        
    except Exception as e:
        return get_error_response(f'生成SM2密钥对失败: {str(e)}')

@crypto_tools_bp.route('/sm2/encrypt', methods=['POST'])
def sm2_encrypt():
    """SM2加密"""
    if not HAS_GMSSL:
        return get_error_response('gmssl库未安装')
    
    try:
        data = request.get_json()
        if not data or 'plaintext' not in data or 'public_key' not in data:
            return get_error_response('请提供plaintext和public_key字段')
        
        plaintext = data['plaintext']
        public_key = data['public_key']
        encoding = data.get('encoding', 'utf-8')
        
        # SM2加密
        encrypter = sm2.CryptSM2(public_key=public_key, private_key=None)
        ciphertext = encrypter.encrypt(plaintext.encode(encoding))
        
        return jsonify({
            'success': True,
            'ciphertext': ciphertext.hex(),
            'plaintext_length': len(plaintext),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'SM2加密失败: {str(e)}')

@crypto_tools_bp.route('/sm2/decrypt', methods=['POST'])
def sm2_decrypt():
    """SM2解密"""
    if not HAS_GMSSL:
        return get_error_response('gmssl库未安装')
    
    try:
        data = request.get_json()
        if not data or 'ciphertext' not in data or 'private_key' not in data:
            return get_error_response('请提供ciphertext和private_key字段')
        
        ciphertext_hex = data['ciphertext']
        private_key = data['private_key']
        public_key = data.get('public_key', '')  # SM2解密需要公钥
        encoding = data.get('encoding', 'utf-8')
        
        # SM2解密
        decrypter = sm2.CryptSM2(public_key=public_key, private_key=private_key)
        plaintext = decrypter.decrypt(hex_to_bytes(ciphertext_hex))
        
        return jsonify({
            'success': True,
            'plaintext': plaintext.decode(encoding),
            'ciphertext_length': len(ciphertext_hex) // 2,
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'SM2解密失败: {str(e)}')

@crypto_tools_bp.route('/sm2/sign', methods=['POST'])
def sm2_sign():
    """SM2签名"""
    if not HAS_GMSSL:
        return get_error_response('gmssl库未安装')
    
    try:
        data = request.get_json()
        if not data or 'message' not in data or 'private_key' not in data:
            return get_error_response('请提供message和private_key字段')
        
        message = data['message']
        private_key = data['private_key']
        encoding = data.get('encoding', 'utf-8')
        
        # SM2签名
        signer = sm2.CryptSM2(public_key='', private_key=private_key)
        signature = signer.sign(message.encode(encoding))
        
        return jsonify({
            'success': True,
            'signature': signature.hex(),
            'message_length': len(message),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'SM2签名失败: {str(e)}')

@crypto_tools_bp.route('/sm2/verify', methods=['POST'])
def sm2_verify():
    """SM2验证签名"""
    if not HAS_GMSSL:
        return get_error_response('gmssl库未安装')
    
    try:
        data = request.get_json()
        if not data or 'message' not in data or 'signature' not in data or 'public_key' not in data:
            return get_error_response('请提供message、signature和public_key字段')
        
        message = data['message']
        signature_hex = data['signature']
        public_key = data['public_key']
        encoding = data.get('encoding', 'utf-8')
        
        # SM2验证签名
        verifier = sm2.CryptSM2(public_key=public_key, private_key='')
        is_valid = verifier.verify(hex_to_bytes(signature_hex), message.encode(encoding))
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message_length': len(message),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'SM2验证签名失败: {str(e)}')

# SM4相关功能
@crypto_tools_bp.route('/sm4/encrypt', methods=['POST'])
def sm4_encrypt():
    """SM4加密"""
    if not HAS_GMSSL:
        return get_error_response('gmssl库未安装')
    
    try:
        data = request.get_json()
        if not data or 'plaintext' not in data or 'key' not in data:
            return get_error_response('请提供plaintext和key字段')
        
        plaintext = data['plaintext']
        key_hex = data['key']
        mode = data.get('mode', 'ECB')
        encoding = data.get('encoding', 'utf-8')
        
        # 检查密钥长度
        if len(key_hex) != 32:
            return get_error_response('SM4密钥长度必须为32字节(16字节的十六进制表示)')
        
        # 创建SM4加密器
        cipher = sm4.CryptSM4()
        key = hex_to_bytes(key_hex)
        cipher.set_key(key, sm4.SM4_ENCRYPT)
        
        # 加密
        if mode == 'ECB':
            ciphertext = cipher.crypt_ecb(plaintext.encode(encoding))
        elif mode == 'CBC':
            # 生成随机IV
            from os import urandom
            iv = urandom(16)
            ciphertext = cipher.crypt_cbc(iv, plaintext.encode(encoding))
            return jsonify({
                'success': True,
                'ciphertext': ciphertext.hex(),
                'iv': iv.hex(),
                'mode': mode,
                'plaintext_length': len(plaintext),
                'encoding': encoding
            }), 200
        else:
            return get_error_response(f'不支持的模式: {mode}')
        
        return jsonify({
            'success': True,
            'ciphertext': ciphertext.hex(),
            'mode': mode,
            'plaintext_length': len(plaintext),
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'SM4加密失败: {str(e)}')

@crypto_tools_bp.route('/sm4/decrypt', methods=['POST'])
def sm4_decrypt():
    """SM4解密"""
    if not HAS_GMSSL:
        return get_error_response('gmssl库未安装')
    
    try:
        data = request.get_json()
        if not data or 'ciphertext' not in data or 'key' not in data:
            return get_error_response('请提供ciphertext和key字段')
        
        ciphertext_hex = data['ciphertext']
        key_hex = data['key']
        mode = data.get('mode', 'ECB')
        iv_hex = data.get('iv')
        encoding = data.get('encoding', 'utf-8')
        
        # 检查密钥长度
        if len(key_hex) != 32:
            return get_error_response('SM4密钥长度必须为32字节(16字节的十六进制表示)')
        
        # 创建SM4解密器
        cipher = sm4.CryptSM4()
        key = hex_to_bytes(key_hex)
        cipher.set_key(key, sm4.SM4_DECRYPT)
        
        # 解密
        ciphertext = hex_to_bytes(ciphertext_hex)
        if mode == 'ECB':
            plaintext = cipher.crypt_ecb(ciphertext)
        elif mode == 'CBC':
            if not iv_hex:
                return get_error_response('CBC模式需要提供IV')
            iv = hex_to_bytes(iv_hex)
            plaintext = cipher.crypt_cbc(iv, ciphertext)
        else:
            return get_error_response(f'不支持的模式: {mode}')
        
        return jsonify({
            'success': True,
            'plaintext': plaintext.decode(encoding),
            'ciphertext_length': len(ciphertext),
            'mode': mode,
            'encoding': encoding
        }), 200
        
    except Exception as e:
        return get_error_response(f'SM4解密失败: {str(e)}')
