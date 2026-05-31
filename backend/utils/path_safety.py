import os
from typing import Optional
from werkzeug.utils import secure_filename


def sanitize_filename(filename: str) -> str:
    if not filename:
        return ''

    basename = os.path.basename(filename)
    safe = secure_filename(basename)

    if not safe:
        safe = 'unnamed_file'

    return safe


def safe_join(base_dir: str, filename: str) -> Optional[str]:
    real_base = os.path.realpath(base_dir)
    safe_name = sanitize_filename(filename)
    if not safe_name:
        return None

    target = os.path.realpath(os.path.join(real_base, safe_name))

    if not target.startswith(real_base + os.sep) and target != real_base:
        return None

    return target
