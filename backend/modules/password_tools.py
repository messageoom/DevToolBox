from flask import Blueprint, request, jsonify
import secrets
import string
import re
import logging

try:
    from ..utils.error_handler import safe_error
except ImportError:
    from backend.utils.error_handler import safe_error

logger = logging.getLogger(__name__)

password_tools_bp = Blueprint('password_tools', __name__)

# Character sets
UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = '!@#$%^&*()_+-=[]{}|;:\',.<>?/'

# Ambiguous characters
AMBIGUOUS_CHARS = set('lI1O0')

# Common weak patterns
COMMON_PATTERNS = [
    'password', '123456', 'qwerty', 'abc123', 'letmein',
    'admin', 'welcome', 'monkey', 'master', 'dragon',
    'login', 'princess', 'football', 'shadow', 'sunshine',
    'trustno1', 'iloveyou', 'batman', 'access', 'hello',
    'charlie', 'donald', '123456789', 'password1', 'qwerty123'
]

# Built-in word list for passphrase generation (~200 common English words)
WORD_LIST = [
    'apple', 'banana', 'cherry', 'grape', 'lemon',
    'orange', 'peach', 'plum', 'berry', 'melon',
    'ocean', 'river', 'lake', 'stream', 'pond',
    'mountain', 'valley', 'forest', 'desert', 'island',
    'sunset', 'sunrise', 'rainbow', 'storm', 'breeze',
    'cloud', 'thunder', 'lightning', 'frost', 'snow',
    'tiger', 'eagle', 'dolphin', 'wolf', 'bear',
    'lion', 'fox', 'deer', 'owl', 'hawk',
    'bridge', 'tower', 'castle', 'garden', 'palace',
    'temple', 'harbor', 'lighthouse', 'cottage', 'fortress',
    'silver', 'golden', 'crystal', 'marble', 'ivory',
    'amber', 'jade', 'ruby', 'sapphire', 'emerald',
    'rocket', 'compass', 'anchor', 'shield', 'sword',
    'lantern', 'mirror', 'prism', 'puzzle', 'voyage',
    'horizon', 'summit', 'nexus', 'cipher', 'quantum',
    'stellar', 'aurora', 'nebula', 'cosmic', 'zenith',
    'harmony', 'rhythm', 'melody', 'echo', 'tempo',
    'canvas', 'mosaic', 'fresco', 'origami', 'sonnet',
    'maple', 'cedar', 'willow', 'bamboo', 'cypress',
    'coral', 'pearl', 'shell', 'wave', 'tide',
    'flame', 'ember', 'spark', 'blaze', 'glow',
    'velvet', 'silk', 'cotton', 'linen', 'satin',
    'journey', 'quest', 'wander', 'explore', 'discover',
    'swift', 'agile', 'brave', 'calm', 'bright',
    'noble', 'vivid', 'serene', 'gentle', 'mighty',
    'pepper', 'cinnamon', 'ginger', 'vanilla', 'mint',
    'thunder', 'cyclone', 'tornado', 'blizzard', 'monsoon',
    'piano', 'violin', 'guitar', 'flute', 'drum',
    'crimson', 'scarlet', 'violet', 'indigo', 'azure',
    'spring', 'summer', 'autumn', 'winter', 'season',
    'phoenix', 'griffin', 'dragon', 'unicorn', 'pegasus',
    'atlas', 'orion', 'vega', 'lyra', 'draco'
]


def _build_charset(uppercase, lowercase, numbers, symbols, exclude_ambiguous):
    """Build the character pool and required character sets."""
    charset = ''
    required_sets = []

    if uppercase:
        chars = UPPERCASE
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in AMBIGUOUS_CHARS)
        charset += chars
        required_sets.append(chars)

    if lowercase:
        chars = LOWERCASE
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in AMBIGUOUS_CHARS)
        charset += chars
        required_sets.append(chars)

    if numbers:
        chars = DIGITS
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in AMBIGUOUS_CHARS)
        charset += chars
        required_sets.append(chars)

    if symbols:
        charset += SYMBOLS
        required_sets.append(SYMBOLS)

    return charset, required_sets


@password_tools_bp.route('/generate', methods=['POST'])
def generate_password():
    """Generate cryptographically secure passwords."""
    try:
        data = request.get_json() or {}

        length = data.get('length', 16)
        uppercase = data.get('uppercase', True)
        lowercase = data.get('lowercase', True)
        numbers = data.get('numbers', True)
        symbols = data.get('symbols', True)
        exclude_ambiguous = data.get('exclude_ambiguous', False)
        count = data.get('count', 1)

        # Validate parameters
        if not isinstance(length, int) or length < 8 or length > 128:
            return jsonify({'error': '密码长度必须在8-128之间', 'success': False}), 400

        if not isinstance(count, int) or count < 1 or count > 50:
            return jsonify({'error': '生成数量必须在1-50之间', 'success': False}), 400

        # Ensure at least one character set is enabled
        if not any([uppercase, lowercase, numbers, symbols]):
            return jsonify({'error': '至少需要启用一种字符类型', 'success': False}), 400

        charset, required_sets = _build_charset(uppercase, lowercase, numbers, symbols, exclude_ambiguous)

        if not charset:
            return jsonify({'error': '可用字符集为空', 'success': False}), 400

        # Ensure length is at least the number of required sets
        effective_length = max(length, len(required_sets))

        passwords = []
        for _ in range(count):
            password_chars = []

            # Ensure at least one character from each enabled set
            for req_set in required_sets:
                password_chars.append(secrets.choice(req_set))

            # Fill the rest with random characters from the full charset
            remaining = effective_length - len(password_chars)
            for _ in range(remaining):
                password_chars.append(secrets.choice(charset))

            # Shuffle the characters using cryptographically secure method
            for i in range(len(password_chars) - 1, 0, -1):
                j = secrets.randbelow(i + 1)
                password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

            passwords.append(''.join(password_chars))

        # Build charset info
        excluded_list = list(AMBIGUOUS_CHARS) if exclude_ambiguous else []

        return jsonify({
            'success': True,
            'passwords': passwords,
            'length': effective_length,
            'count': count,
            'charset_info': {
                'uppercase': uppercase,
                'lowercase': lowercase,
                'numbers': numbers,
                'symbols': symbols,
                'excluded_ambiguous': excluded_list
            }
        }), 200

    except Exception as e:
        return safe_error(e)


@password_tools_bp.route('/strength', methods=['POST'])
def check_strength():
    """Evaluate password strength."""
    try:
        data = request.get_json() or {}
        password = data.get('password', '')

        if not password:
            return jsonify({'error': '请输入密码', 'success': False}), 400

        score = 0
        suggestions = []

        # Length scoring
        pwd_len = len(password)
        if pwd_len < 8:
            score -= 20
            suggestions.append('密码长度应至少8个字符')
        elif pwd_len <= 12:
            score += 0
            suggestions.append('建议使用12个字符以上的密码')
        elif pwd_len <= 16:
            score += 10
        elif pwd_len <= 24:
            score += 20
        else:
            score += 30

        # Character type scoring
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_numbers = bool(re.search(r'\d', password))
        has_symbols = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:\',.<>?/`~"\\]', password))

        if has_lowercase:
            score += 10
        else:
            suggestions.append('建议包含小写字母')

        if has_uppercase:
            score += 10
        else:
            suggestions.append('建议包含大写字母')

        if has_numbers:
            score += 10
        else:
            suggestions.append('建议包含数字')

        if has_symbols:
            score += 15
        else:
            suggestions.append('建议包含特殊符号以提高安全性')

        # Check for repeated characters (>30% same character)
        if pwd_len > 0:
            char_counts = {}
            for c in password:
                char_counts[c] = char_counts.get(c, 0) + 1
            max_count = max(char_counts.values())
            if max_count / pwd_len > 0.3:
                score -= 15
                suggestions.append('避免过多重复字符')

        # Check for sequential characters (abc, 123, etc.)
        sequential_count = 0
        for i in range(len(password) - 2):
            c1, c2, c3 = ord(password[i]), ord(password[i + 1]), ord(password[i + 2])
            if c2 - c1 == 1 and c3 - c2 == 1:
                sequential_count += 1
            elif c1 - c2 == 1 and c2 - c3 == 1:
                sequential_count += 1
        if sequential_count > 0:
            score -= 10
            suggestions.append('避免连续字符（如abc、123）')

        # Check for common patterns
        password_lower = password.lower()
        found_common = False
        for pattern in COMMON_PATTERNS:
            if pattern in password_lower:
                found_common = True
                break
        if found_common:
            score -= 25
            suggestions.append('避免使用常见密码模式')

        # Clamp score to 0-100
        score = max(0, min(100, score))

        # Determine level
        if score <= 20:
            level = '极弱'
        elif score <= 40:
            level = '弱'
        elif score <= 60:
            level = '中'
        elif score <= 80:
            level = '强'
        else:
            level = '极强'

        # Add general suggestion if score is not perfect
        if not suggestions and score < 100:
            suggestions.append('密码强度良好，可以考虑进一步增加长度')

        return jsonify({
            'success': True,
            'score': score,
            'level': level,
            'length': pwd_len,
            'has_uppercase': has_uppercase,
            'has_lowercase': has_lowercase,
            'has_numbers': has_numbers,
            'has_symbols': has_symbols,
            'suggestions': suggestions
        }), 200

    except Exception as e:
        return safe_error(e)


@password_tools_bp.route('/passphrase', methods=['POST'])
def generate_passphrase():
    """Generate a mnemonic passphrase."""
    try:
        data = request.get_json() or {}

        word_count = data.get('word_count', 4)
        separator = data.get('separator', '-')
        capitalize = data.get('capitalize', False)
        include_number = data.get('include_number', False)

        # Validate parameters
        if not isinstance(word_count, int) or word_count < 3 or word_count > 12:
            return jsonify({'error': '单词数量必须在3-12之间', 'success': False}), 400

        # Select random words
        words = [secrets.choice(WORD_LIST) for _ in range(word_count)]

        # Apply capitalization
        if capitalize:
            words = [w.capitalize() for w in words]

        # Append a random digit to one random word
        if include_number:
            idx = secrets.randbelow(len(words))
            words[idx] = words[idx] + str(secrets.randbelow(10))

        passphrase = separator.join(words)

        return jsonify({
            'success': True,
            'passphrase': passphrase,
            'words': words,
            'word_count': word_count,
            'separator': separator,
            'capitalize': capitalize,
            'include_number': include_number
        }), 200

    except Exception as e:
        return safe_error(e)
