"""路径安全:sanitize_filename / safe_join —— 含中文文件名保留(本次修复的核心)。"""
import os
from utils.path_safety import sanitize_filename, safe_join


def test_sanitize_filename_preserves_chinese():
    """中文文件名必须完整保留(原 secure_filename 会破坏成只剩扩展名)。"""
    assert sanitize_filename('中文文档.pdf') == '中文文档.pdf'
    assert sanitize_filename('报告.docx') == '报告.docx'
    assert sanitize_filename('我的照片.jpg') == '我的照片.jpg'
    assert sanitize_filename('photo 备份.jpg') == 'photo 备份.jpg'


def test_sanitize_filename_security_path_traversal():
    assert sanitize_filename('../../../etc/passwd') == 'passwd'
    assert sanitize_filename('..\\..\\windows\\system32') == 'system32'


def test_sanitize_filename_security_edge_cases():
    assert sanitize_filename('..') == 'unnamed_file'
    assert sanitize_filename('.') == 'unnamed_file'
    assert sanitize_filename('   ') == 'unnamed_file'
    assert sanitize_filename('') == ''
    assert sanitize_filename('file\x00name.txt') == 'filename.txt'  # NULL 字节
    assert sanitize_filename('a:b/c*d?e') == 'cde'  # Windows 保留字符


def test_safe_join_keeps_target_inside_base(tmp_path):
    base = str(tmp_path)
    result = safe_join(base, '中文文档.pdf')
    assert result == os.path.realpath(os.path.join(base, '中文文档.pdf'))


def test_safe_join_normalizes_traversal(tmp_path):
    base = str(tmp_path)
    # 路径遍历被 basename 提取 + realpath 规范化,结果仍限定在 base 内
    result = safe_join(base, '../../../etc/passwd')
    assert result is not None
    assert result.startswith(os.path.realpath(base))
