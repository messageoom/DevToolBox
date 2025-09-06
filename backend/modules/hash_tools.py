from flask import Blueprint, request, jsonify
import hashlib
import hmac

# 尝试导入额外的哈希库
try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    blake3 = None
    HAS_BLAKE3 = False

# 尝试另一种方式导入blake3
if not HAS_BLAKE3:
    try:
        from blake3 import blake3 as b3_function
        HAS_BLAKE3 = True
        blake3 = type('blake3', (), {'blake3': b3_function})
    except ImportError:
        HAS_BLAKE3 = False
        blake3 = None

try:
    HAS_SM3 = 'sm3' in hashlib.algorithms_available
except:
    HAS_SM3 = False

print(f"HAS_BLAKE3: {HAS_BLAKE3}")
print(f"blake3 module: {blake3}")
print(f"HAS_SM3: {HAS_SM3}")

hash_tools_bp = Blueprint('hash_tools', __name__)

# 支持的哈希算法
SUPPORTED_ALGORITHMS = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha224': hashlib.sha224,
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512,
    'sha3_224': hashlib.sha3_224,
    'sha3_256': hashlib.sha3_256,
    'sha3_384': hashlib.sha3_384,
    'sha3_512': hashlib.sha3_512,
    'blake2b': hashlib.blake2b,
    'blake2s': hashlib.blake2s
}

# 动态添加SM3算法（如果可用）
if HAS_SM3:
    SUPPORTED_ALGORITHMS['sm3'] = lambda: hashlib.new('sm3')
    print("Added SM3 to SUPPORTED_ALGORITHMS")

# 动态添加BLAKE3算法（如果可用）
print(f"Adding BLAKE3: HAS_BLAKE3={HAS_BLAKE3}, blake3 is not None={blake3 is not None}")
if HAS_BLAKE3 and blake3 is not None:
    SUPPORTED_ALGORITHMS['blake3'] = lambda: blake3.blake3()
    print("Added BLAKE3 to SUPPORTED_ALGORITHMS")
else:
    print("BLAKE3 not added to SUPPORTED_ALGORITHMS")

print(f"Final SUPPORTED_ALGORITHMS keys: {list(SUPPORTED_ALGORITHMS.keys())}")

@hash_tools_bp.route('/algorithms', methods=['GET'])
def get_algorithms():
    """获取支持的哈希算法"""
    return jsonify({
        'success': True,
        'algorithms': list(SUPPORTED_ALGORITHMS.keys())
    }), 200

@hash_tools_bp.route('/generate', methods=['POST'])
def generate_hash():
    """生成哈希值"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': '请提供text字段'}), 400

        text = data['text']
        algorithm = data.get('algorithm', 'sha256').lower()
        encoding = data.get('encoding', 'utf-8')

        # 调试信息
        print(f"Requested algorithm: {algorithm}")
        print(f"Supported algorithms: {list(SUPPORTED_ALGORITHMS.keys())}")
        print(f"Algorithm in supported: {algorithm in SUPPORTED_ALGORITHMS}")

        if algorithm not in SUPPORTED_ALGORITHMS:
            return jsonify({'error': f'不支持的算法: {algorithm}'}), 400

        try:
            # 生成哈希
            hash_obj = SUPPORTED_ALGORITHMS[algorithm]()
            hash_obj.update(text.encode(encoding))
            hash_value = hash_obj.hexdigest()

            return jsonify({
                'success': True,
                'algorithm': algorithm,
                'hash': hash_value,
                'length': len(hash_value),
                'input_length': len(text),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hash_tools_bp.route('/generate-file', methods=['POST'])
def generate_file_hash():
    """生成文件哈希值"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['file']
        algorithm = request.form.get('algorithm', 'sha256').lower()

        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        if algorithm not in SUPPORTED_ALGORITHMS:
            return jsonify({'error': f'不支持的算法: {algorithm}'}), 400

        try:
            # 生成文件哈希
            hash_obj = SUPPORTED_ALGORITHMS[algorithm]()
            file_content = file.read()
            hash_obj.update(file_content)
            hash_value = hash_obj.hexdigest()

            return jsonify({
                'success': True,
                'filename': file.filename,
                'algorithm': algorithm,
                'hash': hash_value,
                'length': len(hash_value),
                'file_size': len(file_content),
                'mime_type': file.mimetype or 'application/octet-stream'
            }), 200

        except Exception as e:
            return jsonify({'error': f'文件处理错误: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hash_tools_bp.route('/verify', methods=['POST'])
def verify_hash():
    """验证哈希值"""
    try:
        data = request.get_json()
        if not data or 'text' not in data or 'hash' not in data:
            return jsonify({'error': '请提供text和hash字段'}), 400

        text = data['text']
        expected_hash = data['hash']
        algorithm = data.get('algorithm', 'sha256').lower()
        encoding = data.get('encoding', 'utf-8')

        if algorithm not in SUPPORTED_ALGORITHMS:
            return jsonify({'error': f'不支持的算法: {algorithm}'}), 400

        try:
            # 生成哈希并比较
            hash_obj = SUPPORTED_ALGORITHMS[algorithm]()
            hash_obj.update(text.encode(encoding))
            actual_hash = hash_obj.hexdigest()

            is_valid = hmac.compare_digest(actual_hash, expected_hash)

            return jsonify({
                'success': True,
                'valid': is_valid,
                'algorithm': algorithm,
                'expected_hash': expected_hash,
                'actual_hash': actual_hash,
                'input_length': len(text),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hash_tools_bp.route('/hmac', methods=['POST'])
def generate_hmac():
    """生成HMAC"""
    try:
        data = request.get_json()
        if not data or 'text' not in data or 'key' not in data:
            return jsonify({'error': '请提供text和key字段'}), 400

        text = data['text']
        key = data['key']
        algorithm = data.get('algorithm', 'sha256').lower()
        encoding = data.get('encoding', 'utf-8')

        if algorithm not in SUPPORTED_ALGORITHMS:
            return jsonify({'error': f'不支持的算法: {algorithm}'}), 400

        try:
            # 生成HMAC
            hmac_obj = hmac.new(
                key.encode(encoding),
                text.encode(encoding),
                SUPPORTED_ALGORITHMS[algorithm]
            )
            hmac_value = hmac_obj.hexdigest()

            return jsonify({
                'success': True,
                'algorithm': algorithm,
                'hmac': hmac_value,
                'length': len(hmac_value),
                'input_length': len(text),
                'key_length': len(key),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hash_tools_bp.route('/pbkdf2', methods=['POST'])
def generate_pbkdf2():
    """生成PBKDF2哈希"""
    try:
        data = request.get_json()
        if not data or 'password' not in data or 'salt' not in data:
            return jsonify({'error': '请提供password和salt字段'}), 400

        password = data['password']
        salt = data['salt']
        algorithm = data.get('algorithm', 'sha256').lower()
        iterations = data.get('iterations', 100000)
        dklen = data.get('dklen')  # 派生密钥长度
        encoding = data.get('encoding', 'utf-8')

        if algorithm not in SUPPORTED_ALGORITHMS:
            return jsonify({'error': f'不支持的算法: {algorithm}'}), 400

        try:
            # 生成PBKDF2
            derived_key = hashlib.pbkdf2_hmac(
                algorithm,
                password.encode(encoding),
                salt.encode(encoding),
                iterations,
                dklen
            )
            derived_hex = derived_key.hex()

            return jsonify({
                'success': True,
                'algorithm': algorithm,
                'derived_key': derived_hex,
                'length': len(derived_hex),
                'iterations': iterations,
                'salt': salt,
                'password_length': len(password),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hash_tools_bp.route('/bcrypt', methods=['POST'])
def generate_bcrypt():
    """生成bcrypt哈希"""
    try:
        import bcrypt

        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({'error': '请提供password字段'}), 400

        password = data['password']
        rounds = data.get('rounds', 12)
        encoding = data.get('encoding', 'utf-8')

        try:
            # 生成bcrypt哈希
            hashed = bcrypt.hashpw(password.encode(encoding), bcrypt.gensalt(rounds))
            hashed_str = hashed.decode('ascii')

            return jsonify({
                'success': True,
                'hash': hashed_str,
                'rounds': rounds,
                'password_length': len(password),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except ImportError:
        return jsonify({'error': 'bcrypt模块未安装，请安装bcrypt'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@hash_tools_bp.route('/bcrypt/verify', methods=['POST'])
def verify_bcrypt():
    """验证bcrypt哈希"""
    try:
        import bcrypt

        data = request.get_json()
        if not data or 'password' not in data or 'hash' not in data:
            return jsonify({'error': '请提供password和hash字段'}), 400

        password = data['password']
        hash_value = data['hash']
        encoding = data.get('encoding', 'utf-8')

        try:
            # 验证bcrypt哈希
            is_valid = bcrypt.checkpw(
                password.encode(encoding),
                hash_value.encode('ascii')
            )

            return jsonify({
                'success': True,
                'valid': is_valid,
                'password_length': len(password),
                'encoding': encoding
            }), 200

        except UnicodeEncodeError as e:
            return jsonify({'error': f'编码错误: {str(e)}'}), 400

    except ImportError:
        return jsonify({'error': 'bcrypt模块未安装，请安装bcrypt'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
