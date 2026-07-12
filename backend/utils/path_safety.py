import os
import re
import unicodedata
from typing import Optional


# 文件名中不允许出现的字符:控制字符、路径分隔符、Windows 保留字符
# 注意:这里不使用 werkzeug 的 secure_filename —— 它会通过 ascii 编码
# 丢弃所有非 ASCII 字符(包括中文),导致中文文件名被破坏成只剩扩展名。
_UNSAFE_FILENAME_RE = re.compile(r'[\x00-\x1f\x7f<>:"/\\|?*]')


def sanitize_filename(filename: str) -> str:
    """清理文件名,使其在文件系统上安全可用,同时保留中文等 Unicode 字符。

    与 werkzeug.secure_filename 不同,本函数不会丢弃非 ASCII 字符,
    仅移除路径分隔符、控制字符等真正危险的字符。
    """
    if not filename:
        return ''

    # 统一把反斜杠当作路径分隔符,防止 Windows 风格路径绕过 basename
    basename = filename.replace('\\', '/').rsplit('/', 1)[-1]

    # NFKC 规范化:统一全角/半角字符,防止利用全角字符绕过过滤
    basename = unicodedata.normalize('NFKC', basename)

    # 去除危险字符(路径分隔符、控制字符、Windows 保留字符)
    basename = _UNSAFE_FILENAME_RE.sub('', basename)

    # 去除首尾空格和点(防止隐藏文件 / 父目录引用,例如 ".." 或 ".")
    basename = basename.strip().strip('.')

    if not basename:
        return 'unnamed_file'

    return basename


def safe_join(base_dir: str, filename: str) -> Optional[str]:
    real_base = os.path.realpath(base_dir)
    safe_name = sanitize_filename(filename)
    if not safe_name:
        return None

    target = os.path.realpath(os.path.join(real_base, safe_name))

    if not target.startswith(real_base + os.sep) and target != real_base:
        return None

    return target
